"""
Module de formatage compact pour un affichage optimisé en espace.

Ce module fournit un formateur condensé qui affiche les métriques essentielles
dans un format très compact, idéal pour les terminaux étroits, les barres de
statut ou les affichages où l'espace est limité. Il utilise des symboles et
des abréviations pour maximiser l'information dans un minimum d'espace.
"""

from typing import Dict, Any

from formatters.base import BaseFormatter
from config import ANSI_COLORS, BYTES_PER_GB


class CompactFormatter(BaseFormatter):
    """
    Formateur compact pour un affichage condensé des données.
    
    Cette classe hérite de BaseFormatter et implémente un formatage très
    compact des données de monitoring, utilisant des abréviations et des
    symboles pour minimiser l'espace utilisé tout en restant informatif.
    
    Attributes:
        show_timestamp (bool): Indique si l'horodatage doit être affiché.
        Hérite tous les autres attributs de BaseFormatter.
    """
    
    def __init__(self, color: bool = True, show_timestamp: bool = True) -> None:
        """
        Initialise le formateur compact.
        
        Args:
            color: Active ou désactive la coloration ANSI (défaut : True).
            show_timestamp: Active ou désactive l'affichage de l'horodatage
                           (défaut : True).
        """
        super().__init__(color)
        self.show_timestamp = show_timestamp
        
    def format_monitoring_data(self, data: Dict[str, Any]) -> str:
        """
        Formate les données de monitoring en format compact.
        
        Cette méthode crée une ligne compacte contenant toutes les métriques
        essentielles séparées par des barres verticales. Les valeurs sont
        abrégées (CPU, RAM, DSK, GPU) pour gagner de l'espace.
        
        Args:
            data: Dictionnaire contenant les données de monitoring avec la structure :
                  {
                      'timestamp': str,
                      'data': {
                          'processor': {'usage_percent': float},
                          'memory': {...},
                          'disk': {...},
                          'gpu': {...}  # Optionnel
                      }
                  }
        
        Returns:
            Une chaîne compacte sur une ligne avec toutes les métriques.
            Format : "[HH:MM:SS] CPU:XX% │ RAM:XX%(X.X/XXG) │ DSK:XX% [│ GPU:XX%/XX%]"
        """
        monitoring = data.get('data', {})
        timestamp = data.get('timestamp', '')
        
        # Extraction des métriques principales
        cpu = monitoring['processor']['usage_percent']
        ram = monitoring['memory']['percentage']
        ram_used_gb = monitoring['memory']['used'] / BYTES_PER_GB
        ram_total_gb = monitoring['memory']['total'] / BYTES_PER_GB
        disk = monitoring['disk']['percentage']
        
        # Construction de la sortie compacte
        parts = []
        
        # Ajout de l'horodatage si activé
        if self.show_timestamp:
            # Extraction de l'heure uniquement (format HH:MM:SS)
            time_part = timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp
            parts.append(f"[{time_part}]")
            
        # Ajout des métriques principales avec format abrégé
        parts.extend([
            f"CPU:{self._format_compact_metric(cpu)}",
            f"RAM:{self._format_compact_metric(ram)}({ram_used_gb:.1f}/{ram_total_gb:.0f}G)",
            f"DSK:{self._format_compact_metric(disk)}"
        ])
        
        # Ajout des informations GPU si disponibles
        if 'gpu' in monitoring and monitoring['gpu']:
            gpu = monitoring['gpu']
            gpu_usage = gpu['gpu_usage_percent']
            gpu_mem = gpu['memory_percentage']
            # Format GPU : utilisation/mémoire
            parts.append(f"GPU:{self._format_compact_metric(gpu_usage)}/{self._format_compact_metric(gpu_mem)}")
            
        return " │ ".join(parts)
        
    def format_connection_message(self, message: str) -> str:
        """
        Formate les messages de connexion de manière compacte.
        
        Cette méthode utilise un symbole de flèche (►) pour indiquer
        visuellement un message de connexion, coloré en bleu pour
        une identification rapide.
        
        Args:
            message: Le message de connexion à formater.
        
        Returns:
            Le message formaté avec symbole et coloration bleue.
        
        Example:
            >>> formatter = CompactFormatter()
            >>> print(formatter.format_connection_message("Connected"))
            ► Connected  # En bleu
        """
        return self._colorize(f"► {message}", ANSI_COLORS['BLUE'])
        
    def format_error(self, error: str) -> str:
        """
        Formate les messages d'erreur de manière compacte.
        
        Cette méthode utilise un symbole de croix (✗) pour indiquer
        visuellement une erreur, coloré en rouge pour attirer
        immédiatement l'attention.
        
        Args:
            error: Le message d'erreur à formater.
        
        Returns:
            Le message d'erreur formaté avec symbole et coloration rouge.
        
        Example:
            >>> formatter = CompactFormatter()
            >>> print(formatter.format_error("Connection failed"))
            ✗ Connection failed  # En rouge
        """
        return self._colorize(f"✗ {error}", ANSI_COLORS['RED'])
        
    def _format_compact_metric(self, value: float) -> str:
        """
        Formate une métrique de manière compacte avec couleur.
        
        Cette méthode privée formate une valeur de pourcentage dans
        un format très compact (3 caractères + %) avec une coloration
        basée sur le niveau d'utilisation.
        
        Args:
            value: La valeur de la métrique en pourcentage.
        
        Returns:
            La valeur formatée sur 3 caractères plus le symbole %,
            avec coloration appropriée.
        
        Note:
            Le format utilisé est {:3.0f}% pour garantir un alignement
            cohérent dans l'affichage compact.
        """
        formatted = f"{value:3.0f}%"
        color = self._get_usage_color(value)
        return self._colorize(formatted, color)