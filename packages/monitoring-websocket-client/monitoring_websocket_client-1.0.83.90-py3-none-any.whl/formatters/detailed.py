"""
Module de formatage détaillé pour un affichage complet des données de monitoring.

Ce module fournit un formateur complet qui affiche toutes les informations
disponibles sur le système de manière structurée et visuellement attractive.
Il inclut des barres de progression, des codes couleur et une organisation
hiérarchique des données pour une lecture facile et informative.
"""

from typing import Dict, Any
from datetime import datetime

from formatters.base import BaseFormatter
from monitoring_config import (
    ANSI_COLORS,
    BYTES_PER_MB,
    PROGRESS_BAR_LENGTH,
    DIVIDER_LENGTH,
    DIVIDER_CHAR,
    TIME_FORMAT
)


class DetailedFormatter(BaseFormatter):
    """
    Formateur détaillé pour un affichage complet des informations système.
    
    Cette classe hérite de BaseFormatter et implémente un formatage riche
    des données de monitoring avec barres de progression, codes couleur et
    organisation hiérarchique. Elle est idéale pour les tableaux de bord
    détaillés ou les rapports de monitoring complets.
    
    Attributes:
        Hérite tous les attributs de BaseFormatter.
    """
    
    def format_monitoring_data(self, data: Dict[str, Any]) -> str:
        """
        Formate les données de monitoring avec informations détaillées.
        
        Cette méthode crée un affichage structuré et complet de toutes les
        métriques système disponibles, incluant CPU, mémoire, disque, GPU
        (si disponible) et informations système. Chaque section est visuellement
        séparée et utilise des barres de progression pour les pourcentages.
        
        Args:
            data: Dictionnaire contenant les données de monitoring avec la structure :
                  {
                      'timestamp': str,
                      'data': {
                          'processor': {...},
                          'memory': {...},
                          'disk': {...},
                          'gpu': {...},  # Optionnel
                          'system': {...}
                      }
                  }
        
        Returns:
            Une chaîne multi-lignes formatée contenant toutes les informations
            système organisées par sections avec codes couleur et barres de
            progression.
        
        Example:
            >>> formatter = DetailedFormatter()
            >>> data = {'timestamp': '2024-01-01 12:00:00', 'data': {...}}
            >>> print(formatter.format_monitoring_data(data))
            === System Monitoring - 2024-01-01 12:00:00 ===
            CPU Information:
              Usage: 45.2% [████████░░░░░░░░░░░░]
            ...
        """
        timestamp = data.get('timestamp', '')
        monitoring = data.get('data', {})
        
        # Construction de l'en-tête avec horodatage
        lines = [
            "",
            self._colorize(f"=== System Monitoring - {timestamp} ===", ANSI_COLORS['CYAN']),
            ""
        ]
        
        # Section Informations CPU
        cpu = monitoring.get('processor', {})
        system = monitoring.get('system', {})
        lines.extend([
            self._colorize("CPU Information:", ANSI_COLORS['MAGENTA']),
            f"  Usage: {self._format_percentage(cpu.get('usage_percent', 0))}",
            f"  Cores: {cpu.get('logical_count', 'N/A')} (Physical: {cpu.get('core_count', 'N/A')})",
            f"  Architecture: {system.get('architecture', 'N/A')}",
            f"  Current Frequency: {cpu.get('frequency_current', 0):.0f} MHz",
            f"  Max Frequency: {cpu.get('frequency_max', 0):.0f} MHz",
            ""
        ])
        
        # Section Informations Mémoire
        memory = monitoring.get('memory', {})
        lines.extend([
            self._colorize("Memory Information:", ANSI_COLORS['MAGENTA']),
            f"  Usage: {self._format_percentage(memory.get('percentage', 0))}",
            f"  Used: {self._format_bytes(memory.get('used', 0))} / {self._format_bytes(memory.get('total', 0))}",
            f"  Available: {self._format_bytes(memory.get('available', 0))}",
            ""
        ])
        
        # Section Informations Disque
        disk = monitoring.get('disk', {})
        lines.extend([
            self._colorize("Disk Information:", ANSI_COLORS['MAGENTA']),
            f"  Usage: {self._format_percentage(disk.get('percentage', 0))}",
            f"  Used: {self._format_bytes(disk.get('used', 0))} / {self._format_bytes(disk.get('total', 0))}",
            f"  Free: {self._format_bytes(disk.get('free', 0))}",
            f"  Mount: {disk.get('mount_point', 'N/A')}",
            ""
        ])
        
        # Section Informations GPU (si disponible)
        if 'gpu' in monitoring and monitoring['gpu']:
            gpu = monitoring['gpu']
            lines.extend([
                self._colorize("GPU Information:", ANSI_COLORS['MAGENTA']),
                f"  Name: {gpu.get('name', 'N/A')}",
                f"  Usage: {self._format_percentage(gpu.get('gpu_usage_percent', 0))}",
                f"  Memory: {self._format_percentage(gpu.get('memory_percentage', 0))} "
                f"({self._format_bytes(gpu.get('memory_used', 0) * BYTES_PER_MB)} / "
                f"{self._format_bytes(gpu.get('memory_total', 0) * BYTES_PER_MB)})",
            ])
            # Ajout de la température si disponible
            if gpu.get('temperature') is not None:
                lines.append(f"  Temperature: {gpu['temperature']:.0f}°C")
            lines.append("")
            
        # Section Informations Système
        lines.extend([
            self._colorize("System Information:", ANSI_COLORS['MAGENTA']),
            f"  OS: {system.get('os_name', 'N/A')} {system.get('os_version', '')}",
            f"  Hostname: {system.get('hostname', 'N/A')}",
            f"  Platform: {system.get('platform', 'N/A')}",
            self._colorize(DIVIDER_CHAR * DIVIDER_LENGTH, ANSI_COLORS['CYAN'])
        ])
        
        return '\n'.join(lines)
        
    def format_connection_message(self, message: str) -> str:
        """
        Formate les messages de statut de connexion avec horodatage.
        
        Cette méthode ajoute un horodatage précis et un préfixe CONNECTION
        coloré en bleu pour distinguer les messages de connexion dans les logs.
        
        Args:
            message: Le message de connexion à formater.
        
        Returns:
            Le message formaté avec horodatage et coloration bleue.
        
        Example:
            >>> formatter = DetailedFormatter()
            >>> print(formatter.format_connection_message("Connected to server"))
            [2024-01-01 12:00:00] CONNECTION: Connected to server  # En bleu
        """
        timestamp = datetime.now().strftime(TIME_FORMAT)
        return self._colorize(f"[{timestamp}] CONNECTION: {message}", ANSI_COLORS['BLUE'])
        
    def format_error(self, error: str) -> str:
        """
        Formate les messages d'erreur avec horodatage.
        
        Cette méthode ajoute un horodatage précis et un préfixe ERROR
        coloré en rouge pour mettre en évidence les erreurs dans les logs.
        
        Args:
            error: Le message d'erreur à formater.
        
        Returns:
            Le message d'erreur formaté avec horodatage et coloration rouge.
        
        Example:
            >>> formatter = DetailedFormatter()
            >>> print(formatter.format_error("Connection lost"))
            [2024-01-01 12:00:00] ERROR: Connection lost  # En rouge
        """
        timestamp = datetime.now().strftime(TIME_FORMAT)
        return self._colorize(f"[{timestamp}] ERROR: {error}", ANSI_COLORS['RED'])
        
    def _format_percentage(self, value: float) -> str:
        """
        Formate un pourcentage avec couleur et barre de progression.
        
        Cette méthode privée crée une représentation visuelle attractive
        d'un pourcentage en combinant la valeur numérique avec une barre
        de progression colorée selon le niveau d'utilisation.
        
        Args:
            value: La valeur du pourcentage (0-100).
        
        Returns:
            Une chaîne contenant le pourcentage formaté et une barre de
            progression colorée. Format : "XX.X% [████████░░░░░░░░░░░░]"
        
        Note:
            La longueur de la barre est définie par PROGRESS_BAR_LENGTH.
            Les caractères utilisés sont █ (plein) et ░ (vide).
        """
        color = self._get_usage_color(value)
        percentage_str = f"{value:5.1f}%"
        
        # Création de la barre de progression
        bar_length = PROGRESS_BAR_LENGTH
        filled = int(value / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return f"{self._colorize(percentage_str, color)} [{self._colorize(bar, color)}]"