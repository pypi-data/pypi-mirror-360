"""
Classe de base pour les formateurs.

Ce module définit la classe abstraite de base pour tous les formateurs
de sortie, fournissant l'interface commune et les méthodes utilitaires
partagées par tous les formateurs concrets.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from config import (
    BYTES_PER_KB,
    SECONDS_PER_MINUTE,
    SECONDS_PER_HOUR,
    THRESHOLD_WARNING,
    THRESHOLD_CRITICAL,
    ANSI_COLORS
)


class BaseFormatter(ABC):
    """Classe abstraite de base pour les formateurs de sortie.
    
    Cette classe définit l'interface que tous les formateurs doivent implémenter
    et fournit des méthodes utilitaires communes pour le formatage des données.
    
    Attributes:
        color: Active ou désactive l'utilisation des codes couleur ANSI.
    """
    
    def __init__(self, color: bool = True) -> None:
        """Initialise le formateur de base.
        
        Args:
            color: Active l'utilisation des couleurs ANSI si True.
        """
        self.color = color
        
    @abstractmethod
    def format_monitoring_data(self, data: Dict[str, Any]) -> str:
        """Formate les données de monitoring pour l'affichage.
        
        Args:
            data: Dictionnaire contenant les données de monitoring.
            
        Returns:
            str: Chaîne formatée prête à afficher.
        """
        pass
        
    @abstractmethod
    def format_connection_message(self, message: str) -> str:
        """Formate les messages de statut de connexion.
        
        Args:
            message: Message de connexion à formater.
            
        Returns:
            str: Message formaté.
        """
        pass
        
    @abstractmethod
    def format_error(self, error: str) -> str:
        """Formate les messages d'erreur.
        
        Args:
            error: Message d'erreur à formater.
            
        Returns:
            str: Message d'erreur formaté.
        """
        pass
        
    def format_statistics(self, stats: Dict[str, Any]) -> str:
        """Formate les statistiques du client.
        
        Args:
            stats: Dictionnaire contenant les statistiques.
            
        Returns:
            str: Statistiques formatées pour l'affichage.
        """
        lines = [
            "\n=== Statistiques du Client ===",
            f"Messages: {stats['messages_received']} reçus, {stats['messages_sent']} envoyés",
            f"Données: {self._format_bytes(stats['bytes_received'])} reçus, {self._format_bytes(stats['bytes_sent'])} envoyés",
            f"Durée de fonctionnement: {self._format_duration(stats.get('uptime_seconds', 0))}",
            f"Reconnexions: {stats['reconnect_attempts']}",
            f"Erreurs: {stats['error_count']}"
        ]
        return '\n'.join(lines)
        
    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Formate les octets en format lisible par l'humain.
        
        Args:
            bytes_count: Nombre d'octets à formater.
            
        Returns:
            str: Taille formatée avec unité appropriée.
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < BYTES_PER_KB:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= BYTES_PER_KB
        return f"{bytes_count:.1f} TB"
        
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Formate une durée en secondes en format lisible.
        
        Args:
            seconds: Durée en secondes.
            
        Returns:
            str: Durée formatée (heures, minutes, secondes).
        """
        if seconds < SECONDS_PER_MINUTE:
            return f"{seconds:.0f}s"
        elif seconds < SECONDS_PER_HOUR:
            return f"{seconds/SECONDS_PER_MINUTE:.0f}m {seconds%SECONDS_PER_MINUTE:.0f}s"
        else:
            hours = seconds / SECONDS_PER_HOUR
            minutes = (seconds % SECONDS_PER_HOUR) / SECONDS_PER_MINUTE
            return f"{hours:.0f}h {minutes:.0f}m"
            
    def _colorize(self, text: str, color_code: str) -> str:
        """Applique une couleur au texte si les couleurs sont activées.
        
        Args:
            text: Texte à coloriser.
            color_code: Code couleur ANSI.
            
        Returns:
            str: Texte avec codes couleur ou texte brut.
        """
        if not self.color:
            return text
        return f"\033[{color_code}m{text}\033[0m"
        
    @staticmethod
    def _get_usage_color(percentage: float) -> str:
        """Obtient le code couleur basé sur le pourcentage d'utilisation.
        
        Args:
            percentage: Pourcentage d'utilisation.
            
        Returns:
            str: Code couleur ANSI approprié selon les seuils.
        """
        if percentage >= THRESHOLD_CRITICAL:
            return ANSI_COLORS['RED']
        elif percentage >= THRESHOLD_WARNING:
            return ANSI_COLORS['YELLOW']
        else:
            return ANSI_COLORS['GREEN']