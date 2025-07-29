"""
Gestionnaire de journalisation pour tous les messages.

Ce module implémente un gestionnaire qui enregistre tous les messages WebSocket
dans des fichiers de log, avec support de la rotation automatique des fichiers
lorsqu'ils atteignent une taille limite.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Gère les différents contextes d'import
import os
import sys

# Essaye d'importer config depuis différents emplacements
try:
    from ..config import LOG_ROTATION_SIZE, LOG_FILENAME_PATTERN, TIMESTAMP_FORMAT
except ImportError:
    try:
        from config import LOG_ROTATION_SIZE, LOG_FILENAME_PATTERN, TIMESTAMP_FORMAT
    except ImportError:
        # Ajoute le répertoire parent au chemin et réessaye
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        from config import LOG_ROTATION_SIZE, LOG_FILENAME_PATTERN, TIMESTAMP_FORMAT


class LoggingHandler:
    """Gestionnaire qui enregistre tous les messages dans un fichier.
    
    Cette classe fournit un mécanisme pour enregistrer tous les messages WebSocket
    dans des fichiers de log, avec rotation automatique et statistiques de suivi.
    
    Attributes:
        log_file: Chemin du fichier de log actuel.
        logger: Logger pour les messages internes.
        log_raw: Enregistre les messages bruts si True.
        rotate_size: Taille maximale avant rotation.
        message_count: Compteur de messages enregistrés.
        file_handler: Gestionnaire de fichier de logging.
        file_logger: Logger dédié pour l'écriture dans le fichier.
    """
    
    def __init__(
        self,
        log_file: Optional[Path] = None,
        logger: Optional[logging.Logger] = None,
        log_raw: bool = True,
        rotate_size: Optional[int] = LOG_ROTATION_SIZE
    ) -> None:
        """Initialise le gestionnaire de journalisation.
        
        Args:
            log_file: Chemin du fichier de log (généré automatiquement si None).
            logger: Logger pour les messages internes.
            log_raw: Si True, enregistre les messages JSON bruts.
            rotate_size: Taille en octets pour déclencher la rotation.
        """
        self.log_file = log_file or Path(LOG_FILENAME_PATTERN.format(timestamp=datetime.now().strftime(TIMESTAMP_FORMAT)))
        self.logger = logger or logging.getLogger(__name__)
        self.log_raw = log_raw
        self.rotate_size = rotate_size
        self.message_count = 0
        
        # Configure la journalisation dans le fichier
        self._setup_file_logging()
        
    def _setup_file_logging(self) -> None:
        """Configure le gestionnaire de journalisation de fichier.
        
        Crée un nouveau gestionnaire de fichier et le configure avec
        le formateur approprié pour l'enregistrement des messages.
        """
        self.file_handler = logging.FileHandler(self.log_file)
        self.file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        
        # Crée un logger séparé pour la sortie fichier
        self.file_logger = logging.getLogger(f"{__name__}.file")
        self.file_logger.addHandler(self.file_handler)
        self.file_logger.setLevel(logging.DEBUG)
        
    async def handle_all_messages(self, data: Dict[str, Any]) -> None:
        """Enregistre tous les messages entrants.
        
        Vérifie si une rotation est nécessaire et enregistre le message
        selon le mode configuré (brut ou formaté).
        
        Args:
            data: Dictionnaire contenant les données du message.
        """
        self.message_count += 1
        
        # Vérifie si une rotation est nécessaire
        if self.rotate_size and self.log_file.exists():
            if self.log_file.stat().st_size > self.rotate_size:
                self._rotate_log()
                
        # Enregistre le message
        if self.log_raw:
            self.file_logger.info(json.dumps(data))
        else:
            message_type = data.get('type', 'unknown')
            timestamp = data.get('timestamp', datetime.now().isoformat())
            self.file_logger.info(f"[{message_type}] {timestamp} - Message #{self.message_count}")
            
    def _rotate_log(self) -> None:
        """Effectue la rotation du fichier de log quand il devient trop gros.
        
        Ferme le fichier actuel, le renomme avec un horodatage,
        et crée un nouveau fichier de log.
        """
        # Ferme le gestionnaire actuel
        self.file_handler.close()
        self.file_logger.removeHandler(self.file_handler)
        
        # Renomme le fichier actuel
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        new_name = self.log_file.with_name(f"{self.log_file.stem}_{timestamp}{self.log_file.suffix}")
        self.log_file.rename(new_name)
        self.logger.info(f"Rotated log file to {new_name}")
        
        # Configure un nouveau gestionnaire
        self._setup_file_logging()
        
    def get_stats(self) -> Dict[str, Any]:
        """Obtient les statistiques de journalisation.
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant le nombre de messages,
                          le chemin du fichier et sa taille actuelle.
        """
        return {
            'message_count': self.message_count,
            'log_file': str(self.log_file),
            'log_size': self.log_file.stat().st_size if self.log_file.exists() else 0
        }