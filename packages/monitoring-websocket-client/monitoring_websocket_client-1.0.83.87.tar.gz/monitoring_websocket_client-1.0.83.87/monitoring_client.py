"""
Client de monitoring de haut niveau avec support synchrone/asynchrone.

Ce module fournit des interfaces de haut niveau pour le client de monitoring WebSocket,
avec support pour les modes synchrone et asynchrone, la gestion des callbacks,
et l'intégration avec les formateurs et gestionnaires.
"""

import os
import sys

# Ajoute le répertoire du projet au chemin Python pour l'import de la configuration
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import asyncio
import logging
import threading
from pathlib import Path
from typing import Optional, Union, Dict, Any, Callable, List
from datetime import datetime

from .websocket_client import WebSocketClient, ClientState
from .formatters import (
    BaseFormatter,
    SimpleFormatter,
    DetailedFormatter,
    JsonFormatter,
    CompactFormatter
)
from .handlers import MonitoringHandler, LoggingHandler
from .config import (
    DEFAULT_WEBSOCKET_URI,
    DEFAULT_FORMAT_TYPE,
    RECONNECT_INTERVAL,
    PING_INTERVAL,
    WAIT_LOOP_SLEEP_INTERVAL,
    WAIT_LOOP_MAX_ITERATIONS,
    STOP_TIMEOUT,
    THREAD_JOIN_TIMEOUT,
    SEND_TIMEOUT
)


class MonitoringClient:
    """
    Client de monitoring de haut niveau utilisable en contexte synchrone et asynchrone.
    
    Cette classe fournit une interface simplifiée pour le client WebSocket,
    avec gestion automatique des formateurs, des gestionnaires et des callbacks.
    
    Example async usage:
        async with MonitoringClient('ws://localhost:8765') as client:
            await client.start()
            # Le client s'exécute en arrière-plan
            await asyncio.sleep(60)
            
    Example sync usage:
        with MonitoringClient('ws://localhost:8765', sync_mode=True) as client:
            client.start()
            # Le client s'exécute dans un thread séparé
            time.sleep(60)
    """
    
    def __init__(
        self,
        uri: str = DEFAULT_WEBSOCKET_URI,
        format_type: str = DEFAULT_FORMAT_TYPE,
        color: bool = True,
        reconnect: bool = True,
        reconnect_interval: float = RECONNECT_INTERVAL,
        max_reconnect_attempts: Optional[int] = None,
        ping_interval: float = PING_INTERVAL,
        save_data: Optional[Union[str, Path]] = None,
        store_history: bool = False,
        sync_mode: bool = False,
        logger: Optional[logging.Logger] = None,
        on_message: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_connect: Optional[Callable[[], None]] = None,
        on_disconnect: Optional[Callable[[], None]] = None
    ):
        """
        Initialise le client de monitoring.
        
        Args:
            uri: URI WebSocket de connexion.
            format_type: Format de sortie ('simple', 'detailed', 'compact', 'json').
            color: Active la sortie en couleur.
            reconnect: Active la reconnexion automatique.
            reconnect_interval: Secondes entre les tentatives de reconnexion.
            max_reconnect_attempts: Nombre maximum de tentatives de reconnexion (None pour infini).
            ping_interval: Secondes entre les messages ping.
            save_data: Chemin pour sauvegarder toutes les données reçues.
            store_history: Stocke l'historique des messages en mémoire.
            sync_mode: Exécute en mode synchrone (pour les environnements non-async).
            logger: Instance de logger à utiliser.
            on_message: Callback pour les messages de données de monitoring.
            on_error: Callback pour les erreurs.
            on_connect: Callback lors de la connexion.
            on_disconnect: Callback lors de la déconnexion.
        """
        self.uri = uri
        self.format_type = format_type
        self.color = color
        self.sync_mode = sync_mode
        self.logger = logger or logging.getLogger(__name__)
        
        # Création du formateur
        self.formatter = MonitoringClient._create_formatter(format_type, color)
        
        # Création des gestionnaires
        self.monitoring_handler = MonitoringHandler(
            formatter=self.formatter,
            logger=self.logger,
            store_history=store_history
        )
        
        self.logging_handler = None
        if save_data:
            self.logging_handler = LoggingHandler(
                log_file=Path(save_data),
                logger=self.logger
            )
        
        # Création du client WebSocket
        self.ws_client = WebSocketClient(
            uri=uri,
            logger=self.logger,
            reconnect=reconnect,
            reconnect_interval=reconnect_interval,
            max_reconnect_attempts=max_reconnect_attempts,
            ping_interval=ping_interval
        )
        
        # Callbacks utilisateur
        self._on_message = on_message
        self._on_error = on_error
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        
        # Enregistrement des gestionnaires
        self._setup_handlers()
        
        # Support du mode synchrone
        self._sync_thread = None
        self._sync_loop = None
        self._running = False
        
    @staticmethod
    def _create_formatter(format_type: str, color: bool) -> BaseFormatter:
        """Crée un formateur basé sur le type.
        
        Args:
            format_type: Type de formateur à créer.
            color: Active les couleurs dans le formateur.
            
        Returns:
            BaseFormatter: Instance du formateur approprié.
        """
        formatters = {
            'simple': SimpleFormatter,
            'detailed': DetailedFormatter,
            'compact': CompactFormatter,
            'json': JsonFormatter
        }
        
        formatter_class = formatters.get(format_type, SimpleFormatter)
        
        if formatter_class == JsonFormatter:
            return formatter_class(pretty=True)
        else:
            return formatter_class(color=color)
            
    def _setup_handlers(self) -> None:
        """Configure les gestionnaires d'événements WebSocket.
        
        Enregistre tous les gestionnaires nécessaires pour traiter les messages
        WebSocket, les changements d'état et les callbacks utilisateur.
        """
        # Gestionnaire des données de monitoring
        async def handle_monitoring_data(data: Dict[str, Any]) -> None:
            await self.monitoring_handler.handle_monitoring_data(data)
            if self._on_message:
                if asyncio.iscoroutinefunction(self._on_message):
                    await self._on_message(data)
                else:
                    self._on_message(data)
                    
        self.ws_client.on('monitoring_data', handle_monitoring_data)
        self.ws_client.on('connection', self.monitoring_handler.handle_connection)
        
        # Gestionnaire de journalisation
        if self.logging_handler:
            self.ws_client.on('*', self.logging_handler.handle_all_messages)
            
        # Gestionnaire de changement d'état
        async def on_state_change(old_state: ClientState, new_state: ClientState) -> None:
            message = f"State: {old_state.value} -> {new_state.value}"
            self.logger.info(message)
            
            # Appelle les callbacks utilisateur
            if new_state.value == 'connected' and self._on_connect:
                if asyncio.iscoroutinefunction(self._on_connect):
                    await self._on_connect()
                else:
                    self._on_connect()
            elif new_state.value == 'disconnected' and self._on_disconnect:
                if asyncio.iscoroutinefunction(self._on_disconnect):
                    await self._on_disconnect()
                else:
                    self._on_disconnect()
                    
        self.ws_client.on('state_change', on_state_change)
        
    # Méthodes asynchrones
    
    async def start_async(self) -> None:
        """Démarre le client (version asynchrone).
        
        Lance la boucle principale du client WebSocket en mode asynchrone.
        """
        self._running = True
        await self.ws_client.run()
        
    async def stop_async(self) -> None:
        """Arrête le client (version asynchrone).
        
        Ferme proprement la connexion WebSocket et arrête toutes les tâches.
        """
        self._running = False
        await self.ws_client.disconnect()
        
    async def send_async(self, data: Dict[str, Any]) -> None:
        """Envoie un message (version asynchrone).
        
        Args:
            data: Dictionnaire de données à envoyer.
        """
        await self.ws_client.send(data)
        
    # Méthodes synchrones
    
    def _run_in_thread(self) -> None:
        """Exécute le client asynchrone dans un thread séparé.
        
        Crée une nouvelle boucle d'événements dans le thread et exécute
        le client asynchrone, permettant l'utilisation en mode synchrone.
        """
        self._sync_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._sync_loop)
        
        try:
            self._sync_loop.run_until_complete(self.start_async())
        except Exception as e:
            self.logger.error(f"Error in sync thread: {e}")
            if self._on_error:
                self._on_error(e)
        finally:
            self._sync_loop.close()
            
    def start(self) -> None:
        """Démarre le client (version synchrone).
        
        Lance le client dans un thread séparé et attend la connexion.
        
        Raises:
            RuntimeError: Si le client est déjà en cours d'exécution ou
                         si appelé en mode asynchrone.
        """
        if self.sync_mode:
            if self._sync_thread and self._sync_thread.is_alive():
                raise RuntimeError("Client is already running")
                
            self._sync_thread = threading.Thread(target=self._run_in_thread)
            self._sync_thread.daemon = True
            self._sync_thread.start()
            
            # Attend la connexion
            import time
            for _ in range(WAIT_LOOP_MAX_ITERATIONS):  # Wait for connection
                if self.is_connected():
                    break
                time.sleep(WAIT_LOOP_SLEEP_INTERVAL)
        else:
            raise RuntimeError("Use start_async() in async mode or set sync_mode=True")
            
    def stop(self) -> None:
        """Arrête le client (version synchrone).
        
        Arrête proprement le client et attend la fin du thread.
        
        Raises:
            RuntimeError: Si appelé en mode asynchrone.
        """
        if self.sync_mode:
            if self._sync_loop and self._running:
                future = asyncio.run_coroutine_threadsafe(
                    self.stop_async(),
                    self._sync_loop
                )
                future.result(timeout=STOP_TIMEOUT)
                
            if self._sync_thread:
                self._sync_thread.join(timeout=THREAD_JOIN_TIMEOUT)
        else:
            raise RuntimeError("Use stop_async() in async mode or set sync_mode=True")
            
    def send(self, data: Dict[str, Any]) -> None:
        """Envoie un message (version synchrone).
        
        Args:
            data: Dictionnaire de données à envoyer.
            
        Raises:
            RuntimeError: Si le client n'est pas en cours d'exécution ou
                         si appelé en mode asynchrone.
        """
        if self.sync_mode:
            if not self._sync_loop:
                raise RuntimeError("Client is not running")
                
            future = asyncio.run_coroutine_threadsafe(
                self.send_async(data),
                self._sync_loop
            )
            future.result(timeout=SEND_TIMEOUT)
        else:
            raise RuntimeError("Use send_async() in async mode or set sync_mode=True")
            
    # Méthodes communes
    
    def is_connected(self) -> bool:
        """Vérifie si le client est connecté.
        
        Returns:
            bool: True si connecté, False sinon.
        """
        return self.ws_client.state.value == 'connected'
        
    def get_statistics(self) -> Dict[str, Any]:
        """Obtient les statistiques du client.
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant toutes les statistiques.
        """
        stats = self.ws_client.get_statistics()
        
        if self.logging_handler:
            stats['logging'] = self.logging_handler.get_stats()
            
        return stats
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Obtient l'historique des messages si store_history est activé.
        
        Returns:
            List[Dict[str, Any]]: Liste des messages reçus avec horodatage.
        """
        return self.monitoring_handler.get_history()
        
    def get_last_data(self) -> Optional[Dict[str, Any]]:
        """Obtient les dernières données de monitoring reçues.
        
        Returns:
            Optional[Dict[str, Any]]: Dernières données ou None si aucune.
        """
        return self.monitoring_handler.get_last_data()
        
    def set_formatter(self, format_type: str, color: Optional[bool] = None) -> None:
        """Change le formateur de sortie.
        
        Args:
            format_type: Nouveau type de formateur.
            color: Active/désactive les couleurs (None conserve l'état actuel).
        """
        if color is None:
            color = self.color
            
        self.formatter = self._create_formatter(format_type, color)
        self.monitoring_handler.formatter = self.formatter
        self.format_type = format_type
        self.color = color
        
    # Support du gestionnaire de contexte
    
    async def __aenter__(self) -> 'MonitoringClient':
        """Entrée du gestionnaire de contexte asynchrone.
        
        Returns:
            MonitoringClient: Instance du client.
        """
        return self
        
    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Sortie du gestionnaire de contexte asynchrone.
        
        Arrête automatiquement le client si encore actif.
        """
        if self._running:
            await self.stop_async()
            
    def __enter__(self) -> 'MonitoringClient':
        """Entrée du gestionnaire de contexte synchrone.
        
        Returns:
            MonitoringClient: Instance du client.
            
        Raises:
            RuntimeError: Si utilisé en mode asynchrone.
        """
        if not self.sync_mode:
            raise RuntimeError("Use async with for async mode or set sync_mode=True")
        return self
        
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Sortie du gestionnaire de contexte synchrone.
        
        Arrête automatiquement le client si encore actif.
        """
        if self._running:
            self.stop()


class SimpleMonitoringClient(MonitoringClient):
    """
    Client de monitoring simplifié pour les cas d'usage basiques.
    
    Cette classe fournit une interface encore plus simple pour les cas
    d'usage courants, avec connexion/déconnexion directe et callbacks simplifiés.
    
    Example:
        # Usage synchrone
        client = SimpleMonitoringClient()
        client.connect()
        time.sleep(60)
        client.disconnect()
        
        # Avec callback
        def on_data(data):
            print(f"CPU: {data['data']['processor']['usage_percent']}%")
            
        client = SimpleMonitoringClient(on_data=on_data)
        client.connect()
    """
    
    def __init__(
        self,
        uri: str = DEFAULT_WEBSOCKET_URI,
        on_data: Optional[Callable[[Dict[str, Any]], None]] = None,
        format_type: str = DEFAULT_FORMAT_TYPE,
        auto_print: bool = True
    ) -> None:
        """
        Initialise le client simple.
        
        Args:
            uri: URI WebSocket.
            on_data: Callback pour chaque donnée de monitoring.
            format_type: Format de sortie.
            auto_print: Affiche automatiquement les données formatées.
        """
        # Désactive l'affichage si un callback personnalisé est fourni
        if on_data and auto_print:
            auto_print = False
            
        super().__init__(
            uri=uri,
            format_type=format_type,
            sync_mode=True,
            on_message=on_data
        )
        
        self.auto_print = auto_print
        
        # Remplace le gestionnaire de monitoring si pas d'affichage automatique
        if not auto_print:
            async def silent_handler(data: Dict[str, Any]) -> None:
                # Stocke juste les données, sans afficher
                self.monitoring_handler.last_data = data
                if self.monitoring_handler.store_history:
                    self.monitoring_handler.history.append({
                        'timestamp': datetime.now(),
                        'data': data
                    })
                    
            self.ws_client.handlers['monitoring_data'] = [silent_handler]
            if self._on_message:
                self.ws_client.on('monitoring_data', self._on_message)
                
    def connect(self) -> None:
        """Connecte au serveur.
        
        Méthode simplifiée pour démarrer la connexion.
        """
        self.start()
        
    def disconnect(self) -> None:
        """Déconnecte du serveur.
        
        Méthode simplifiée pour arrêter la connexion.
        """
        self.stop()
        
    @staticmethod
    def wait(duration: float) -> None:
        """Attend pendant la durée spécifiée tout en recevant des données.
        
        Args:
            duration: Durée d'attente en secondes.
        """
        import time
        time.sleep(duration)