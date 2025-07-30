"""
Gestionnaire des données de monitoring.

Ce module implémente le gestionnaire principal pour traiter les données
de monitoring reçues via WebSocket, incluant le filtrage, le stockage
de l'historique et le formatage pour l'affichage.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from formatters.base import BaseFormatter
from monitoring_config import MAX_HISTORY_SIZE


class MonitoringHandler:
    """Gestionnaire pour les messages de données de monitoring.
    
    Cette classe traite les messages de monitoring entrants, applique des filtres
    optionnels, maintient un historique des données et formate l'affichage.
    
    Attributes:
        formatter: Formateur pour l'affichage des données.
        logger: Logger pour les messages de débogage.
        filters: Liste de fonctions de filtrage à appliquer.
        store_history: Active le stockage de l'historique.
        max_history: Nombre maximum d'entrées dans l'historique.
        history: Liste des données historiques.
        last_data: Dernières données reçues.
    """
    
    def __init__(
        self,
        formatter: BaseFormatter,
        logger: Optional[logging.Logger] = None,
        filters: Optional[List[Callable[[Dict[str, Any]], bool]]] = None,
        store_history: bool = False,
        max_history: int = MAX_HISTORY_SIZE
    ) -> None:
        """Initialise le gestionnaire de monitoring.
        
        Args:
            formatter: Instance du formateur pour l'affichage.
            logger: Logger optionnel pour les messages.
            filters: Liste de fonctions de filtrage (retournent True pour conserver).
            store_history: Active le stockage de l'historique des données.
            max_history: Taille maximale de l'historique.
        """
        self.formatter = formatter
        self.logger = logger or logging.getLogger(__name__)
        self.filters = filters or []
        self.store_history = store_history
        self.max_history = max_history
        self.history = []
        self.last_data = None
        
    async def handle_monitoring_data(self, data: Dict[str, Any]) -> None:
        """Traite un message de données de monitoring.
        
        Applique les filtres, stocke les données si nécessaire,
        et affiche le résultat formaté.
        
        Args:
            data: Dictionnaire contenant les données de monitoring.
        """
        # Applique les filtres
        for filter_func in self.filters:
            if not filter_func(data):
                return
                
        # Stocke les données
        self.last_data = data
        if self.store_history:
            self.history.append({
                'timestamp': datetime.now(),
                'data': data
            })
            # Limite la taille de l'historique
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
                
        # Formate et affiche
        formatted = self.formatter.format_monitoring_data(data)
        print(formatted)
        
    async def handle_connection(self, data: Dict[str, Any]) -> None:
        """Gère un message de connexion.
        
        Args:
            data: Dictionnaire contenant les informations de connexion.
        """
        message = data.get('message', 'Connected')
        formatted = self.formatter.format_connection_message(message)
        print(formatted)
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Obtient l'historique stocké.
        
        Returns:
            List[Dict[str, Any]]: Copie de l'historique des données.
        """
        return self.history.copy()
        
    def get_last_data(self) -> Optional[Dict[str, Any]]:
        """Obtient les dernières données reçues.
        
        Returns:
            Optional[Dict[str, Any]]: Dernières données ou None si aucune.
        """
        return self.last_data
        
    def clear_history(self) -> None:
        """Efface l'historique stocké.
        
        Réinitialise complètement l'historique des données.
        """
        self.history.clear()