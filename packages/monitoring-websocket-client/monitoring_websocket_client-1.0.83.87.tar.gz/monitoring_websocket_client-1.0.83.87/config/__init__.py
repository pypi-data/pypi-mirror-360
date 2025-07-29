"""
Module de configuration pour le système de monitoring WebSocket.

Ce module regroupe toutes les constantes de configuration utilisées
dans l'ensemble du projet.
"""

from .config import *

__all__ = [
    # Configuration réseau et connexion WebSocket
    'DEFAULT_WEBSOCKET_URI',
    'RECONNECT_INTERVAL',
    'PING_INTERVAL',
    'PING_TIMEOUT',
    'OPERATION_TIMEOUT',
    'STOP_TIMEOUT',
    'THREAD_JOIN_TIMEOUT',
    'SEND_TIMEOUT',
    'MAX_RECONNECT_ATTEMPTS',
    
    # Configuration de l'affichage et du formatage
    'DEFAULT_FORMAT_TYPE',
    'ANSI_COLORS',
    'THRESHOLD_WARNING',
    'THRESHOLD_CRITICAL',
    'METRIC_FORMAT',
    'PROGRESS_BAR_LENGTH',
    'DIVIDER_LENGTH',
    'DIVIDER_CHAR',
    'TIME_FORMAT',
    'JSON_INDENT_LEVEL',
    'DEFAULT_ENCODING',
    
    # Configuration du stockage des données
    'MAX_HISTORY_SIZE',
    'ERROR_HISTORY_LIMIT',
    
    # Configuration des logs
    'LOG_ROTATION_SIZE',
    'DATE_FORMAT',
    'TIMESTAMP_FORMAT',
    'LOG_FORMAT',
    'LOG_FILENAME_PATTERN',
    
    # Configuration des fichiers d'export
    'DEFAULT_CSV_FILENAME',
    
    # Seuils d'alerte pour le monitoring
    'ALERT_THRESHOLDS',
    
    # Constantes de conversion
    'BYTES_PER_KB',
    'BYTES_PER_MB',
    'BYTES_PER_GB',
    'SECONDS_PER_MINUTE',
    'SECONDS_PER_HOUR',
    
    # Configuration des boucles d'attente et des délais
    'EXAMPLE_WAIT_DURATIONS',
    'WAIT_LOOP_SLEEP_INTERVAL',
    'WAIT_LOOP_MAX_ITERATIONS',
    'CLI_POLLING_INTERVAL',
    
    # Configuration des exemples
    'EXAMPLE_WEBSOCKET_URIS',
    'EXAMPLE_RECONNECT_INTERVAL',
    'EXAMPLE_MAX_RECONNECT_ATTEMPTS',
    'EXAMPLE_LOOP_COUNT',
    'EXAMPLE_LOOP_SLEEP',
]