"""
Configuration centrale pour le système de monitoring WebSocket.

Ce fichier contient toutes les constantes de configuration utilisées
dans l'ensemble du projet.
"""

# =============================================================================
# Configuration réseau et connexion WebSocket
# =============================================================================

# URI WebSocket par défaut
DEFAULT_WEBSOCKET_URI = 'ws://localhost:8765'

# Intervalles de connexion (en secondes)
RECONNECT_INTERVAL = 5.0
PING_INTERVAL = 30.0
PING_TIMEOUT = 10.0

# Timeouts d'opération (en secondes)
OPERATION_TIMEOUT = 5.0
STOP_TIMEOUT = 5.0
THREAD_JOIN_TIMEOUT = 5.0
SEND_TIMEOUT = 5.0

# Tentatives de reconnexion
MAX_RECONNECT_ATTEMPTS = None  # None = tentatives infinies

# =============================================================================
# Configuration de l'affichage et du formatage
# =============================================================================

# Format de sortie par défaut
DEFAULT_FORMAT_TYPE = 'simple'

# Codes couleur ANSI
ANSI_COLORS = {
    'RED': '91',
    'GREEN': '92',
    'YELLOW': '93',
    'BLUE': '94',
    'MAGENTA': '95',
    'CYAN': '96'
}

# Seuils d'alerte pour la coloration (en pourcentage)
THRESHOLD_WARNING = 80  # Seuil pour affichage jaune
THRESHOLD_CRITICAL = 90  # Seuil pour affichage rouge

# Format des nombres pour l'affichage des métriques
METRIC_FORMAT = "{:5.1f}"

# Configuration de l'interface utilisateur
PROGRESS_BAR_LENGTH = 20
DIVIDER_LENGTH = 50
DIVIDER_CHAR = '='

# Format d'affichage de l'heure
TIME_FORMAT = '%H:%M:%S'

# Niveau d'indentation JSON
JSON_INDENT_LEVEL = 2

# Encodage par défaut
DEFAULT_ENCODING = 'utf-8'

# =============================================================================
# Configuration du stockage des données
# =============================================================================

# Taille maximale de l'historique des données
MAX_HISTORY_SIZE = 1000

# Nombre d'erreurs récentes à conserver
ERROR_HISTORY_LIMIT = 5

# =============================================================================
# Configuration des logs
# =============================================================================

# Taille de rotation des logs (en octets)
LOG_ROTATION_SIZE = 10 * 1024 * 1024  # 10 MB

# Formats de date et heure
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'

# Format des messages de log
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Nom de fichier de log par défaut
LOG_FILENAME_PATTERN = 'monitoring_{timestamp}.log'

# =============================================================================
# Configuration des fichiers d'export
# =============================================================================

# Nom de fichier CSV par défaut
DEFAULT_CSV_FILENAME = 'donnees_monitoring.csv'

# =============================================================================
# Seuils d'alerte pour le monitoring (exemples)
# =============================================================================

# Seuils d'utilisation des ressources (en pourcentage)
ALERT_THRESHOLDS = {
    'CPU_WARNING': 50,
    'CPU_CRITICAL': 80,
    'MEMORY_CRITICAL': 80,
    'DISK_CRITICAL': 90
}

# =============================================================================
# Constantes de conversion
# =============================================================================

# Conversion d'octets
BYTES_PER_KB = 1024.0
BYTES_PER_MB = BYTES_PER_KB * 1024
BYTES_PER_GB = BYTES_PER_MB * 1024

# Conversion de temps
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600

# =============================================================================
# Configuration des boucles d'attente et des délais
# =============================================================================

# Délais d'attente pour les exemples (en secondes)
EXAMPLE_WAIT_DURATIONS = {
    'SHORT': 2,
    'MEDIUM': 5,
    'LONG': 10,
    'EXTRA_LONG': 30
}

# Intervalle de sommeil pour les boucles d'attente
WAIT_LOOP_SLEEP_INTERVAL = 0.1

# Nombre maximal d'itérations pour les boucles d'attente
WAIT_LOOP_MAX_ITERATIONS = 50

# Intervalle de polling pour la CLI
CLI_POLLING_INTERVAL = 0.1

# =============================================================================
# Configuration des exemples
# =============================================================================

# URIs WebSocket pour les exemples
EXAMPLE_WEBSOCKET_URIS = {
    'DEFAULT': 'ws://localhost:8765',
    'SECONDARY': 'ws://localhost:8766',
    'INVALID': 'ws://localhost:9999'
}

# Paramètres de reconnexion pour les exemples
EXAMPLE_RECONNECT_INTERVAL = 2.0
EXAMPLE_MAX_RECONNECT_ATTEMPTS = 3

# Nombre d'itérations pour les boucles d'exemple
EXAMPLE_LOOP_COUNT = 15
EXAMPLE_LOOP_SLEEP = 1