"""
Module de formatage simple pour l'affichage basique des données de monitoring.

Ce module fournit un formateur minimaliste qui affiche les métriques essentielles
(CPU, RAM, Disque et optionnellement GPU) sur une seule ligne. Il est conçu pour
une sortie concise et facile à lire, idéale pour les dashboards ou les affichages
en temps réel nécessitant peu d'espace.
"""

from typing import Dict, Any

from formatters.base import BaseFormatter
from config import ANSI_COLORS, METRIC_FORMAT


class SimpleFormatter(BaseFormatter):
    """
    Formateur simple pour un affichage minimaliste des données de monitoring.
    
    Cette classe hérite de BaseFormatter et implémente un formatage compact
    des données de monitoring sur une seule ligne. Elle est optimisée pour
    les affichages nécessitant peu d'espace tout en restant informatifs.
    
    Attributes:
        Hérite tous les attributs de BaseFormatter.
    """
    
    def format_monitoring_data(self, data: Dict[str, Any]) -> str:
        """
        Formate les données de monitoring en format simple sur une ligne.
        
        Cette méthode extrait les métriques clés (CPU, RAM, Disque) et les
        affiche sur une seule ligne avec des codes couleur selon leur niveau
        d'utilisation. Si des données GPU sont disponibles, elles sont
        ajoutées à la fin de la ligne.
        
        Args:
            data: Dictionnaire contenant les données de monitoring avec la structure :
                  {
                      'data': {
                          'processor': {'usage_percent': float},
                          'memory': {'percentage': float},
                          'disk': {'percentage': float},
                          'gpu': {...}  # Optionnel
                      }
                  }
        
        Returns:
            Une chaîne formatée contenant toutes les métriques sur une ligne.
            Format : "CPU: XX.X% | RAM: XX.X% | Disk: XX.X% [| GPU: XX.X%]"
        
        Example:
            >>> formatter = SimpleFormatter()
            >>> data = {'data': {'processor': {'usage_percent': 45.2}, ...}}
            >>> print(formatter.format_monitoring_data(data))
            CPU: 45.2% | RAM: 32.1% | Disk: 67.8%
        """
        monitoring = data.get('data', {})
        
        # Extraction des métriques principales
        cpu = monitoring['processor']['usage_percent']
        ram = monitoring['memory']['percentage']
        disk = monitoring['disk']['percentage']
        
        # Construction de la ligne de sortie
        lines = [
            f"CPU: {self._format_metric(cpu)}% | "
            f"RAM: {self._format_metric(ram)}% | "
            f"Disk: {self._format_metric(disk)}%",
        ]
        
        # Ajout des informations GPU si disponibles
        if 'gpu' in monitoring and monitoring['gpu']:
            gpu = monitoring['gpu']
            lines[0] += f" | GPU: {self._format_metric(gpu['gpu_usage_percent'])}%"
            
        return lines[0]
        
    def format_connection_message(self, message: str) -> str:
        """
        Formate les messages de statut de connexion.
        
        Cette méthode ajoute un préfixe [CONN] et applique une couleur bleue
        pour distinguer visuellement les messages de connexion des autres
        types de messages.
        
        Args:
            message: Le message de connexion à formater.
        
        Returns:
            Le message formaté avec préfixe et coloration bleue.
        
        Example:
            >>> formatter = SimpleFormatter()
            >>> print(formatter.format_connection_message("Connected to server"))
            [CONN] Connected to server  # En bleu
        """
        return self._colorize(f"[CONN] {message}", ANSI_COLORS['BLUE'])
        
    def format_error(self, error: str) -> str:
        """
        Formate les messages d'erreur.
        
        Cette méthode ajoute un préfixe [ERROR] et applique une couleur rouge
        pour mettre en évidence visuellement les erreurs et attirer l'attention
        de l'utilisateur.
        
        Args:
            error: Le message d'erreur à formater.
        
        Returns:
            Le message d'erreur formaté avec préfixe et coloration rouge.
        
        Example:
            >>> formatter = SimpleFormatter()
            >>> print(formatter.format_error("Connection lost"))
            [ERROR] Connection lost  # En rouge
        """
        return self._colorize(f"[ERROR] {error}", ANSI_COLORS['RED'])
        
    def _format_metric(self, value: float) -> str:
        """
        Formate une valeur de métrique avec coloration selon le niveau.
        
        Cette méthode privée applique le format numérique défini dans la
        configuration et ajoute une coloration basée sur le niveau d'utilisation
        (vert pour faible, jaune pour moyen, rouge pour élevé).
        
        Args:
            value: La valeur numérique de la métrique (pourcentage).
        
        Returns:
            La valeur formatée avec la précision définie et la couleur appropriée.
        
        Note:
            Les seuils de couleur sont définis dans la méthode _get_usage_color
            de la classe parente BaseFormatter.
        """
        formatted = METRIC_FORMAT.format(value)
        color = self._get_usage_color(value)
        return self._colorize(formatted, color)