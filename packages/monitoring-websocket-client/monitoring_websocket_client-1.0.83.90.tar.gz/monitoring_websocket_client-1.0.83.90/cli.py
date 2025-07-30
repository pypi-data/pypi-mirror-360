#!/usr/bin/env python3
"""
Client de monitoring WebSocket professionnel avec interface CLI.

Ce module fournit une interface en ligne de commande pour le client de monitoring WebSocket.
Il gère les arguments de ligne de commande, la configuration du logging et l'exécution
du client de monitoring avec gestion des signaux et des statistiques.
"""

import argparse
import asyncio
import logging
import signal
import sys
from typing import Optional
import types

from monitoring_client import MonitoringClient
from monitoring_config import (
    DEFAULT_WEBSOCKET_URI,
    DEFAULT_FORMAT_TYPE,
    RECONNECT_INTERVAL,
    PING_INTERVAL,
    DATE_FORMAT,
    LOG_FORMAT,
    CLI_POLLING_INTERVAL
)


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """Configure le système de logging.
    
    Args:
        verbose: Active le mode verbose (niveau DEBUG) si True.
        log_file: Chemin vers le fichier de log optionnel.
        
    Returns:
        logging.Logger: Instance du logger configurée.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configure le logger racine
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT
    )
    
    logger = logging.getLogger('monitoring_client')
    
    # Ajoute un gestionnaire de fichier si spécifié
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            logging.Formatter(LOG_FORMAT)
        )
        logger.addHandler(file_handler)
        
    return logger


class CLIMonitoringClient:
    """Encapsulation CLI pour MonitoringClient.
    
    Cette classe gère l'exécution du client de monitoring depuis la ligne de commande,
    incluant la gestion des signaux, l'arrêt propre et l'affichage des statistiques.
    
    Attributes:
        args: Arguments de ligne de commande parsés.
        logger: Instance du logger pour cette classe.
        client: Instance du client de monitoring.
        _shutdown: Indicateur d'arrêt demandé.
    """
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.logger = setup_logging(args.verbose, args.log_file)
        self.client = None
        self._shutdown = False
        
    async def run(self) -> None:
        """Exécute le client de monitoring.
        
        Lance le client de monitoring avec les paramètres spécifiés,
        gère les signaux d'interruption et affiche les statistiques à la fin.
        
        Raises:
            Exception: En cas d'erreur durant l'exécution du client.
        """
        # Création du client
        self.client = MonitoringClient(
            uri=self.args.uri,
            format_type=self.args.format,
            color=not self.args.no_color,
            reconnect=not self.args.no_reconnect,
            reconnect_interval=self.args.reconnect_interval,
            max_reconnect_attempts=self.args.max_reconnects,
            ping_interval=self.args.ping_interval,
            save_data=self.args.save_data,
            store_history=self.args.history,
            logger=self.logger
        )
        
        # Configuration des gestionnaires de signaux
        def signal_handler(_sig: int, _frame: Optional[types.FrameType]) -> None:
            if not self._shutdown:
                self.logger.info("Received interrupt signal")
                self._shutdown = True
                if self.client:
                    asyncio.create_task(self.client.stop_async())
            
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            print(self.client.formatter.format_connection_message(
                f"Connecting to {self.args.uri}..."
            ))
            
            if self.args.duration:
                # Exécution pour une durée spécifiée
                asyncio.create_task(self.client.start_async())
                await asyncio.sleep(self.args.duration)
                self._shutdown = True
                await self.client.stop_async()
                
            else:
                # Exécution jusqu'à interruption
                await self.client.start_async()
                while not self._shutdown:
                    await asyncio.sleep(CLI_POLLING_INTERVAL)
                
        except Exception as e:
            print(self.client.formatter.format_error(f"Client error: {e}"))
            self.logger.error("Client error", exc_info=True)
            
        finally:
            # Affichage des statistiques si demandé
            if self.args.stats and self.client:
                stats = self.client.get_statistics()
                print(self.client.formatter.format_statistics(stats))
                
                if self.client.logging_handler:
                    log_stats = self.client.logging_handler.get_stats()
                    print(f"\nLogging statistics: {log_stats['message_count']} "
                          f"messages saved to {log_stats['log_file']}")


def main() -> None:
    """Point d'entrée principal du programme.
    
    Parse les arguments de ligne de commande, initialise le client CLI
    et gère les erreurs de niveau supérieur.
    """
    parser = argparse.ArgumentParser(
        description='Client de monitoring WebSocket professionnel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Exemples:
              # Connexion avec format simple
              %(prog)s
              
              # Utilise le format détaillé avec couleurs
              %(prog)s --format detailed
              
              # Sauvegarde toutes les données dans un fichier
              %(prog)s --save-data monitoring.log
              
              # Exécute pendant 60 secondes avec statistiques
              %(prog)s --duration 60 --stats
              
              # Connexion à un serveur personnalisé
              %(prog)s --uri ws://192.168.1.100:8765
              
              # Désactive la reconnexion automatique
              %(prog)s --no-reconnect
              
            Utilisation programmatique:
              from client import MonitoringClient, SimpleMonitoringClient
              
              # Usage asynchrone
              async with MonitoringClient() as client:
                  await client.start_async()
                  
              # Usage synchrone
              client = SimpleMonitoringClient()
              client.connect()
              client.wait(60)
              client.disconnect()
        """
    )
    
    # Options de connexion
    parser.add_argument(
        '--uri', '-u',
        default=DEFAULT_WEBSOCKET_URI,
        help=f'URI WebSocket de connexion (par défaut: {DEFAULT_WEBSOCKET_URI})'
    )
    
    parser.add_argument(
        '--no-reconnect',
        action='store_true',
        help='Désactive la reconnexion automatique'
    )
    
    parser.add_argument(
        '--reconnect-interval',
        type=float,
        default=RECONNECT_INTERVAL,
        help=f'Intervalle de reconnexion en secondes (par défaut: {RECONNECT_INTERVAL})'
    )
    
    parser.add_argument(
        '--max-reconnects',
        type=int,
        help='Nombre maximum de tentatives de reconnexion'
    )
    
    parser.add_argument(
        '--ping-interval',
        type=float,
        default=PING_INTERVAL,
        help=f'Intervalle de ping en secondes (par défaut: {PING_INTERVAL})'
    )
    
    # Options d'affichage
    parser.add_argument(
        '--format', '-f',
        choices=['simple', 'detailed', 'compact', 'json'],
        default=DEFAULT_FORMAT_TYPE,
        help=f'Format de sortie (par défaut: {DEFAULT_FORMAT_TYPE})'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Désactive la sortie en couleur'
    )
    
    # Options de données
    parser.add_argument(
        '--save-data',
        metavar='FILE',
        help='Sauvegarde toutes les données reçues dans un fichier'
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help='Stocke l\'historique des messages en mémoire'
    )
    
    # Options d'exécution
    parser.add_argument(
        '--duration', '-d',
        type=float,
        help='Exécute pendant la durée spécifiée en secondes'
    )
    
    parser.add_argument(
        '--stats', '-s',
        action='store_true',
        help='Affiche les statistiques à la sortie'
    )
    
    # Options de journalisation
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Active la journalisation détaillée'
    )
    
    parser.add_argument(
        '--log-file',
        help='Journalise dans le fichier spécifié'
    )
    
    args = parser.parse_args()
    
    # Exécution du client
    try:
        cli_client = CLIMonitoringClient(args)
        asyncio.run(cli_client.run())
    except KeyboardInterrupt:
        print("\n\nClient stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()