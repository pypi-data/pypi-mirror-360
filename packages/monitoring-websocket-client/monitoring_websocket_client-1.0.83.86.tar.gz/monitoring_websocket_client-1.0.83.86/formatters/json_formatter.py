"""
Module de formatage JSON pour une sortie lisible par machine.

Ce module fournit un formateur qui produit des données au format JSON,
idéal pour l'intégration avec d'autres systèmes, les API, ou tout
traitement automatique des données de monitoring. Il supporte à la fois
le format JSON compact et le format JSON indenté (pretty-print).
"""

import json
from typing import Dict, Any
from .base import BaseFormatter

# Gestion des imports relatifs pour différents contextes d'exécution
try:
    from ..config import JSON_INDENT_LEVEL
except ImportError:
    try:
        from config import JSON_INDENT_LEVEL
    except ImportError:
        # Fallback pour quand le module est importé depuis différents contextes
        # (par exemple lors de tests unitaires ou d'exécution directe)
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config import JSON_INDENT_LEVEL


class JsonFormatter(BaseFormatter):
    """
    Formateur JSON pour la consommation programmatique des données.
    
    Cette classe hérite de BaseFormatter et implémente un formatage JSON
    des données de monitoring. Elle est conçue pour faciliter l'intégration
    avec d'autres systèmes et permet le traitement automatique des données.
    
    Attributes:
        pretty (bool): Active le formatage JSON indenté (pretty-print).
        Hérite tous les autres attributs de BaseFormatter.
    
    Note:
        La coloration ANSI est désactivée par défaut pour ce formateur
        car le JSON est généralement destiné à être traité par des machines.
    """
    
    def __init__(self, color: bool = False, pretty: bool = False) -> None:
        """
        Initialise le formateur JSON.
        
        Args:
            color: Active ou désactive la coloration ANSI (défaut : False).
                   Généralement désactivé pour le JSON car destiné au
                   traitement automatique.
            pretty: Active ou désactive le formatage indenté (défaut : False).
                    Si True, le JSON sera formaté avec indentation pour
                    améliorer la lisibilité humaine.
        """
        super().__init__(color)
        self.pretty = pretty
        
    def format_monitoring_data(self, data: Dict[str, Any]) -> str:
        """
        Formate les données de monitoring au format JSON.
        
        Cette méthode convertit les données de monitoring en une chaîne JSON,
        soit compacte pour une transmission efficace, soit indentée pour une
        meilleure lisibilité humaine selon la configuration.
        
        Args:
            data: Dictionnaire contenant toutes les données de monitoring
                  à convertir en JSON.
        
        Returns:
            Une chaîne JSON représentant les données de monitoring.
            Si pretty=True, le JSON sera indenté selon JSON_INDENT_LEVEL.
        
        Example:
            >>> formatter = JsonFormatter(pretty=True)
            >>> data = {'timestamp': '2024-01-01T12:00:00', 'data': {...}}
            >>> print(formatter.format_monitoring_data(data))
            {
                "timestamp": "2024-01-01T12:00:00",
                "data": {
                    ...
                }
            }
        """
        if self.pretty:
            return json.dumps(data, indent=JSON_INDENT_LEVEL)
        return json.dumps(data)
        
    def format_connection_message(self, message: str) -> str:
        """
        Formate les messages de statut de connexion au format JSON.
        
        Cette méthode crée un objet JSON standardisé pour les messages
        de connexion, avec un type identifiant clairement la nature
        du message pour faciliter le traitement automatique.
        
        Args:
            message: Le message de connexion à formater.
        
        Returns:
            Une chaîne JSON contenant le type et le message.
            Structure : {"type": "connection", "message": "..."}
        
        Example:
            >>> formatter = JsonFormatter()
            >>> print(formatter.format_connection_message("Connected to server"))
            {"type": "connection", "message": "Connected to server"}
        """
        data = {
            "type": "connection",
            "message": message
        }
        if self.pretty:
            return json.dumps(data, indent=JSON_INDENT_LEVEL)
        return json.dumps(data)
        
    def format_error(self, error: str) -> str:
        """
        Formate les messages d'erreur au format JSON.
        
        Cette méthode crée un objet JSON standardisé pour les erreurs,
        permettant un traitement automatique et une journalisation
        structurée des erreurs.
        
        Args:
            error: Le message d'erreur à formater.
        
        Returns:
            Une chaîne JSON contenant le type et l'erreur.
            Structure : {"type": "error", "error": "..."}
        
        Example:
            >>> formatter = JsonFormatter()
            >>> print(formatter.format_error("Connection timeout"))
            {"type": "error", "error": "Connection timeout"}
        """
        data = {
            "type": "error",
            "error": error
        }
        if self.pretty:
            return json.dumps(data, indent=JSON_INDENT_LEVEL)
        return json.dumps(data)
        
    def format_statistics(self, stats: Dict[str, Any]) -> str:
        """
        Formate les statistiques au format JSON.
        
        Cette méthode crée un objet JSON standardisé pour les statistiques
        de monitoring, permettant l'analyse et le traitement automatique
        des données de performance sur la durée.
        
        Args:
            stats: Dictionnaire contenant les statistiques à formater.
        
        Returns:
            Une chaîne JSON contenant le type et les statistiques.
            Structure : {"type": "statistics", "stats": {...}}
        
        Example:
            >>> formatter = JsonFormatter(pretty=True)
            >>> stats = {'messages_received': 100, 'uptime': 3600}
            >>> print(formatter.format_statistics(stats))
            {
                "type": "statistics",
                "stats": {
                    "messages_received": 100,
                    "uptime": 3600
                }
            }
        """
        data = {
            "type": "statistics",
            "stats": stats
        }
        if self.pretty:
            return json.dumps(data, indent=JSON_INDENT_LEVEL)
        return json.dumps(data)