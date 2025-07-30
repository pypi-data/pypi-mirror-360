# Client de Monitoring WebSocket - Documentation Utilisateur

## Table des Matières

1. [Présentation](#présentation)
2. [Installation](#installation)
3. [Démarrage Rapide](#démarrage-rapide)
4. [Interface en Ligne de Commande](#interface-en-ligne-de-commande)
5. [Utilisation Programmatique](#utilisation-programmatique)
6. [Formats de Sortie](#formats-de-sortie)
7. [Gestionnaires de Messages](#gestionnaires-de-messages)
8. [Configuration](#configuration)
9. [Logging et Journalisation](#logging-et-journalisation)
10. [Gestion des Erreurs](#gestion-des-erreurs)
11. [Cas d'Usage Avancés](#cas-dusage-avancés)
12. [WebSocket Client de Bas Niveau](#websocket-client-de-bas-niveau)
13. [Système d'Événements](#système-dévénements)
14. [Gestion des États](#gestion-des-états)
15. [Statistiques Détaillées](#statistiques-détaillées)
16. [Considérations de Performance](#considérations-de-performance)
17. [API de Référence](#api-de-référence)
18. [Protocole de Communication](#protocole-de-communication)
19. [Considérations de Sécurité](#considérations-de-sécurité)
20. [Bonnes Pratiques](#bonnes-pratiques)

---

## Présentation

Le **Client de Monitoring WebSocket** est un système professionnel de surveillance en temps réel qui permet de recevoir, traiter et afficher des données de monitoring via WebSocket. Il offre une interface flexible pour surveiller les métriques système (CPU, RAM, disque, GPU) avec support pour différents formats de sortie et modes d'utilisation.

ce module a été créé pour fonctionné avec le module **WebSocket Monitoring Server** : https://pypi.org/project/monitoring-websocket-server/

### Caractéristiques Principales

- ✅ **Connexion WebSocket robuste** avec reconnexion automatique
- ✅ **Formats de sortie multiples** (Simple, Détaillé, Compact, JSON)
- ✅ **Interface CLI complète** avec de nombreuses options
- ✅ **API programmatique** pour l'intégration dans vos applications
- ✅ **Modes synchrone et asynchrone** selon vos besoins
- ✅ **Gestion avancée des erreurs** et logging complet
- ✅ **Sauvegarde des données** et historique configurable
- ✅ **Statistiques détaillées** de connexion et performance
- ✅ **Extensibilité** via des formateurs et gestionnaires personnalisés

---

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation depuis PyPI

```bash
pip install monitoring-websocket-client
```

### Installation depuis le Code Source

```bash
git clone https://github.com/nmicinvest/monitoring-websocket-client
cd monitoring-websocket-client
pip install -e .
```

### Points d'Entrée

Après installation, le client est accessible via :

```bash
# Commande directe (point d'entrée setuptools)
monitoring-websocket-client --help

# Exécution de module Python
python -m monitoring_websocket_system_client --help

# Exécution directe du script
python cli.py --help
```

### Vérification de l'Installation

```bash
monitoring-websocket-client --help
```

---

## Démarrage Rapide

### 1. Connexion Basique

```bash
# Connexion au serveur par défaut (ws://localhost:8765)
monitoring-websocket-client

# Connexion à un serveur personnalisé
monitoring-websocket-client --uri ws://192.168.1.100:8765
```

### 2. Formats de Sortie

```bash
# Format simple (par défaut)
monitoring-websocket-client --format simple

# Format détaillé avec barres de progression
monitoring-websocket-client --format detailed

# Format compact pour terminaux étroits
monitoring-websocket-client --format compact

# Format JSON pour l'intégration
monitoring-websocket-client --format json
```

### 3. Sauvegarde des Données

```bash
# Sauvegarde toutes les données reçues
monitoring-websocket-client --save-data monitoring.log

# Exécution pendant 60 secondes avec statistiques
monitoring-websocket-client --duration 60 --stats
```

---

## Interface en Ligne de Commande

### Syntaxe Générale

```bash
monitoring-websocket-client [OPTIONS]
```

### Options de Connexion

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `--uri, -u` | URI WebSocket de connexion | `ws://localhost:8765` |
| `--no-reconnect` | Désactive la reconnexion automatique | Activée |
| `--reconnect-interval` | Intervalle de reconnexion (secondes) | `5.0` |
| `--max-reconnects` | Nombre max de tentatives de reconnexion | Illimité |
| `--ping-interval` | Intervalle de ping (secondes) | `30.0` |

### Options d'Affichage

| Option | Description | Valeurs |
|--------|-------------|---------|
| `--format, -f` | Format de sortie | `simple`, `detailed`, `compact`, `json` |
| `--no-color` | Désactive la sortie en couleur | - |

### Options de Données

| Option | Description | Usage |
|--------|-------------|--------|
| `--save-data FILE` | Sauvegarde vers fichier | `--save-data monitoring.log` |
| `--history` | Stocke l'historique en mémoire | - |

### Options d'Exécution

| Option | Description | Usage |
|--------|-------------|--------|
| `--duration, -d` | Durée d'exécution (secondes) | `--duration 60` |
| `--stats, -s` | Affiche les statistiques à la fin | - |

### Options de Journalisation

| Option | Description | Usage |
|--------|-------------|--------|
| `--verbose, -v` | Active le mode verbeux (DEBUG) | - |
| `--log-file` | Fichier de log personnalisé | `--log-file client.log` |

### Exemples d'Utilisation CLI

#### Surveillance Basique

```bash
# Surveillance simple avec couleurs
monitoring-websocket-client

# Surveillance sans couleurs
monitoring-websocket-client --no-color

# Surveillance avec format détaillé
monitoring-websocket-client --format detailed
```

#### Surveillance avec Sauvegarde

```bash
# Sauvegarde en format JSON
monitoring-websocket-client --format json --save-data data.jsonl

# Sauvegarde avec historique en mémoire
monitoring-websocket-client --save-data monitoring.log --history
```

#### Surveillance Temporisée

```bash
# Surveillance pendant 5 minutes
monitoring-websocket-client --duration 300

# Surveillance pendant 1 heure avec statistiques
monitoring-websocket-client --duration 3600 --stats
```

#### Surveillance avec Logging

```bash
# Logging verbeux dans un fichier
monitoring-websocket-client --verbose --log-file debug.log

# Logging normal avec sauvegarde des données
monitoring-websocket-client --log-file client.log --save-data monitoring.log
```

#### Surveillance de Serveur Distant

```bash
# Connexion à un serveur distant
monitoring-websocket-client --uri ws://192.168.1.100:8765

# Connexion avec paramètres personnalisés
monitoring-websocket-client --uri ws://server.example.com:9090 \
  --reconnect-interval 10 \
  --max-reconnects 5 \
  --ping-interval 60
```

---

## Utilisation Programmatique

### Mode Asynchrone

#### Utilisation avec Context Manager

```python
import asyncio
from monitoring_client import MonitoringClient

async def main():
    async with MonitoringClient('ws://localhost:8765') as client:
        # Le client se connecte automatiquement
        await client.start_async()
        
        # Attendre 60 secondes
        await asyncio.sleep(60)
        
        # Récupérer les statistiques
        stats = client.get_statistics()
        print(f"Messages reçus: {stats['messages_received']}")
        
        # Le client se déconnecte automatiquement

asyncio.run(main())
```

#### Utilisation Manuelle

```python
import asyncio
from monitoring_client import MonitoringClient

async def main():
    client = MonitoringClient(
        uri='ws://localhost:8765',
        format_type='json',
        color=False,
        reconnect=True,
        ping_interval=30
    )
    
    try:
        await client.start_async()
        
        # Votre logique ici
        await asyncio.sleep(120)
        
    finally:
        await client.stop_async()

asyncio.run(main())
```

### Mode Synchrone

#### Utilisation avec Context Manager

```python
from monitoring_client import MonitoringClient
import time

def main():
    with MonitoringClient('ws://localhost:8765', sync_mode=True) as client:
        # Le client se connecte automatiquement
        client.start()
        
        # Attendre 60 secondes
        time.sleep(60)
        
        # Récupérer les statistiques
        stats = client.get_statistics()
        print(f"Messages reçus: {stats['messages_received']}")
        
        # Le client se déconnecte automatiquement

main()
```

#### Client Simplifié

```python
from monitoring_client import SimpleMonitoringClient

def process_data(data):
    """Fonction callback pour traiter les données"""
    cpu_usage = data['data']['processor']['usage_percent']
    print(f"CPU: {cpu_usage}%")
    
    if cpu_usage > 80:
        print("⚠️  Alerte: CPU élevé!")

def main():
    client = SimpleMonitoringClient(
        uri='ws://localhost:8765',
        on_data=process_data,  # Callback personnalisé
        auto_print=False       # Désactive l'affichage automatique
    )
    
    try:
        client.connect()
        client.wait(60)  # Attendre 60 secondes
    finally:
        client.disconnect()

main()
```

### Callbacks Personnalisés

#### Callback de Données

```python
from monitoring_client import MonitoringClient

def handle_monitoring_data(data):
    """Gestionnaire pour les données de monitoring"""
    system_data = data['data']
    
    # Traitement CPU
    cpu_usage = system_data['processor']['usage_percent']
    if cpu_usage > 90:
        send_alert(f"CPU critique: {cpu_usage}%")
    
    # Traitement RAM
    ram_usage = system_data['memory']['usage_percent']
    if ram_usage > 85:
        send_alert(f"RAM élevée: {ram_usage}%")
    
    # Sauvegarde en base de données
    save_to_database(system_data)

def handle_connection_event(event_type, message):
    """Gestionnaire pour les événements de connexion"""
    print(f"Connexion: {event_type} - {message}")

client = MonitoringClient(
    uri='ws://localhost:8765',
    on_message=handle_monitoring_data,
    on_connection_event=handle_connection_event
)
```

#### Callback d'Erreur

```python
from monitoring_client import MonitoringClient

def handle_error(error):
    """Gestionnaire d'erreurs personnalisé"""
    print(f"Erreur détectée: {error}")
    
    # Envoyer notification
    send_notification(f"Erreur monitoring: {error}")
    
    # Logger l'erreur
    logger.error(f"Monitoring error: {error}")

client = MonitoringClient(
    uri='ws://localhost:8765',
    on_error=handle_error
)
```

---

## Formats de Sortie

### Format Simple (`simple`)

**Caractéristiques:**
- Sortie sur une ligne
- Codage couleur selon l'usage
- Compact et lisible

**Exemple:**
```
CPU: 45.2% | RAM: 62.8% | Disk: 28.5% | GPU: 15.0%
```

**Configuration:**
```python
client = MonitoringClient(format_type='simple', color=True)
```

### Format Détaillé (`detailed`)

**Caractéristiques:**
- Sortie multi-lignes
- Barres de progression visuelles
- Informations système complètes
- Horodatage

**Exemple:**
```
=== Monitoring System - 14:30:25 ===
🖥️  Processor:
    Usage: 45.2% [████████████▒▒▒▒▒▒▒▒] (Normal)
    
💾 Memory:
    Usage: 62.8% [████████████████▒▒▒▒] (8.2/13.1 GB)
    
💿 Disk:
    Usage: 28.5% [███████▒▒▒▒▒▒▒▒▒▒▒▒▒] (142.5/500 GB)
    
🎮 GPU:
    Usage: 15.0% [███▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒] (Normal)
```

**Configuration:**
```python
client = MonitoringClient(format_type='detailed', color=True)
```

### Format Compact (`compact`)

**Caractéristiques:**
- Ultra-compact pour terminaux étroits
- Séparateurs Unicode
- Données essentielles uniquement

**Exemple:**
```
[14:30:25] CPU:45% │ RAM:63%(8.2/13G) │ DSK:29% │ GPU:15%/45%
```

**Configuration:**
```python
client = MonitoringClient(format_type='compact', color=True)
```

### Format JSON (`json`)

**Caractéristiques:**
- Format machine-readable
- Pas de couleurs
- Structure standardisée
- Parfait pour l'intégration

**Exemple:**
```json
{
  "timestamp": "2024-01-15T14:30:25.123456",
  "type": "monitoring_data",
  "data": {
    "processor": {
      "usage_percent": 45.2,
      "temperature": 65.0
    },
    "memory": {
      "usage_percent": 62.8,
      "used_gb": 8.2,
      "total_gb": 13.1
    },
    "disk": {
      "usage_percent": 28.5,
      "used_gb": 142.5,
      "total_gb": 500.0
    },
    "gpu": {
      "usage_percent": 15.0,
      "memory_percent": 45.0,
      "temperature": 52.0
    }
  }
}
```

**Configuration:**
```python
client = MonitoringClient(format_type='json', color=False)
```

---

## Gestionnaires de Messages

### MonitoringHandler

**Fonction:** Traite les messages de données de monitoring

**Caractéristiques:**
- Filtrage des données
- Stockage de l'historique
- Cache des dernières données
- Affichage formaté

**Configuration:**
```python
from handlers import MonitoringHandler

# Les gestionnaires sont créés automatiquement par MonitoringClient
# Pour un contrôle personnalisé, accéder aux gestionnaires existants :
monitoring_handler = client.monitoring_handler
logging_handler = client.logging_handler  # Si save_data spécifié

# Ou ajouter des gestionnaires personnalisés
client.ws_client.on('monitoring_data', custom_handler)
```

### LoggingHandler

**Fonction:** Enregistre tous les messages dans des fichiers

**Caractéristiques:**
- Rotation automatique des logs
- Logging brut ou formaté
- Statistiques de logging
- Nommage configurable

**Configuration:**
```python
from handlers import LoggingHandler

# LoggingHandler est créé automatiquement si save_data est spécifié
client = MonitoringClient(
    save_data='monitoring.log'  # Crée automatiquement LoggingHandler
)

# Accès au gestionnaire créé
if client.logging_handler:
    stats = client.logging_handler.get_stats()
    print(f"Messages enregistrés: {stats['message_count']}")
```

### Gestionnaire Personnalisé

**Création d'un gestionnaire personnalisé:**

```python
class AlertHandler:
    def __init__(self, threshold=80):
        self.threshold = threshold
        
    def handle_message(self, message):
        if message['type'] == 'monitoring_data':
            data = message['data']
            
            # Vérifier CPU
            cpu_usage = data['processor']['usage_percent']
            if cpu_usage > self.threshold:
                self.send_alert(f"CPU élevé: {cpu_usage}%")
            
            # Vérifier RAM
            ram_usage = data['memory']['usage_percent']
            if ram_usage > self.threshold:
                self.send_alert(f"RAM élevée: {ram_usage}%")
    
    def send_alert(self, message):
        # Votre logique d'alerte
        print(f"🚨 ALERTE: {message}")

# Utilisation
alert_handler = AlertHandler(threshold=85)
client.ws_client.on('monitoring_data', alert_handler.handle_message)
```

---

## Configuration

### Fichier de Configuration

Le système utilise le fichier `config.py` pour toutes les configurations:

```python
# Configuration réseau
DEFAULT_WEBSOCKET_URI = 'ws://localhost:8765'
RECONNECT_INTERVAL = 5.0
PING_INTERVAL = 30.0
PING_TIMEOUT = 10.0
MAX_RECONNECT_ATTEMPTS = None  # Illimité

# Configuration affichage
DEFAULT_FORMAT_TYPE = 'simple'
THRESHOLD_WARNING = 80.0
THRESHOLD_CRITICAL = 90.0
PROGRESS_BAR_LENGTH = 20
TIME_FORMAT = '%H:%M:%S'
JSON_INDENT_LEVEL = 2

# Configuration données
MAX_HISTORY_SIZE = 1000
LOG_ROTATION_SIZE = 10 * 1024 * 1024  # 10MB
ERROR_HISTORY_LIMIT = 5

# Configuration performance
OPERATION_TIMEOUT = 5.0
SEND_TIMEOUT = 5.0
CLI_POLLING_INTERVAL = 0.1
```

### Variables d'Environnement

```bash
# URI WebSocket
export MONITORING_WEBSOCKET_URI=ws://monitoring.example.com:8765

# Format par défaut
export MONITORING_FORMAT=detailed

# Niveau de log
export MONITORING_LOG_LEVEL=DEBUG

# Fichier de log
export MONITORING_LOG_FILE=/var/log/monitoring.log
```

### Configuration Programmatique

```python
from monitoring_client import MonitoringClient

# Configuration complète
client = MonitoringClient(
    uri='ws://localhost:8765',
    format_type='detailed',
    color=True,
    reconnect=True,
    reconnect_interval=10.0,
    max_reconnect_attempts=5,
    ping_interval=60.0,
    save_data='monitoring.log',
    store_history=True,
    logger=my_logger
)
```

---

## Logging et Journalisation

### Niveaux de Log

| Niveau | Description | Utilisation |
|--------|-------------|-------------|
| `DEBUG` | Informations détaillées | Développement, dépannage |
| `INFO` | Informations générales | Fonctionnement normal |
| `WARNING` | Avertissements | Problèmes potentiels |
| `ERROR` | Erreurs | Erreurs récupérables |
| `CRITICAL` | Erreurs critiques | Erreurs graves |

### Configuration du Logging

#### Via CLI

```bash
# Logging normal
monitoring-client --log-file monitoring.log

# Logging verbeux
monitoring-client --verbose --log-file debug.log

# Logging avec sauvegarde
monitoring-client --log-file logs/client.log --save-data data/monitoring.log
```

#### Via Code

```python
import logging
from monitoring_client import MonitoringClient

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('monitoring_client')

# Utilisation avec le client
client = MonitoringClient(
    uri='ws://localhost:8765',
    logger=logger
)
```

### Rotation des Logs

```python
import logging.handlers
from monitoring_client import MonitoringClient

# Logger avec rotation
handler = logging.handlers.RotatingFileHandler(
    'monitoring.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

logger = logging.getLogger('monitoring_client')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

client = MonitoringClient(logger=logger)
```

---

## Gestion des Erreurs

### Types d'Erreurs

#### Erreurs de Connexion

```python
from monitoring_client import MonitoringClient
import websockets.exceptions

try:
    client = MonitoringClient('ws://serveur-invalide:8765')
    client.start()
except websockets.exceptions.ConnectionClosedError as e:
    print(f"Impossible de se connecter: {e}")
    # Logique de fallback
except Exception as e:
    print(f"Erreur de connexion: {e}")
```

#### Erreurs de Timeout

```python
from monitoring_client import MonitoringClient
import asyncio

try:
    client = MonitoringClient()
    client.start()
except asyncio.TimeoutError as e:
    print(f"Timeout: {e}")
    # Réessayer ou alternative
except Exception as e:
    print(f"Erreur: {e}")
```

#### Erreurs de Format

```python
from monitoring_client import MonitoringClient

try:
    client = MonitoringClient(format_type='invalid_format')
except ValueError as e:
    print(f"Format invalide: {e}")
    # Utiliser format par défaut
    client = MonitoringClient(format_type='simple')
except Exception as e:
    print(f"Erreur de configuration: {e}")
```

### Gestion Robuste

```python
import time
from monitoring_client import MonitoringClient

def robust_monitoring():
    max_retries = 5
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            client = MonitoringClient(
                uri='ws://localhost:8765',
                reconnect=True,
                max_reconnect_attempts=3
            )
            
            with client:
                client.start()
                time.sleep(3600)  # Surveiller pendant 1 heure
                
            break  # Succès, sortir de la boucle
            
        except Exception as e:
            print(f"Tentative {attempt + 1} échouée: {e}")
            
            if attempt < max_retries - 1:
                print(f"Nouvelle tentative dans {retry_delay} secondes...")
                time.sleep(retry_delay)
            else:
                print("Toutes les tentatives ont échoué")
                raise

robust_monitoring()
```

---

## Cas d'Usage Avancés

### 1. Monitoring Distribué

```python
import asyncio
from monitoring_client import MonitoringClient

class DistributedMonitoring:
    def __init__(self, servers):
        self.servers = servers
        self.clients = []
        self.data = {}
    
    async def start_monitoring(self):
        tasks = []
        
        for server in self.servers:
            client = MonitoringClient(
                uri=f'ws://{server}:8765',
                on_message=lambda data, srv=server: self.handle_data(srv, data)
            )
            
            self.clients.append(client)
            tasks.append(client.start_async())
        
        await asyncio.gather(*tasks)
    
    def handle_data(self, server, data):
        self.data[server] = data
        self.analyze_cluster_health()
    
    def analyze_cluster_health(self):
        if len(self.data) < len(self.servers):
            return  # Attendre toutes les données
        
        total_cpu = sum(d['data']['processor']['usage_percent'] 
                       for d in self.data.values())
        avg_cpu = total_cpu / len(self.data)
        
        if avg_cpu > 80:
            self.send_cluster_alert(f"CPU cluster élevé: {avg_cpu:.1f}%")
    
    def send_cluster_alert(self, message):
        print(f"🚨 ALERTE CLUSTER: {message}")

# Utilisation
monitors = DistributedMonitoring(['server1', 'server2', 'server3'])
asyncio.run(monitors.start_monitoring())
```

### 2. Monitoring avec Base de Données

```python
import sqlite3
from datetime import datetime
from monitoring_client import MonitoringClient

class DatabaseMonitoring:
    def __init__(self, db_path='monitoring.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                server TEXT,
                cpu_usage REAL,
                ram_usage REAL,
                disk_usage REAL,
                gpu_usage REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_data(self, data):
        conn = sqlite3.connect(self.db_path)
        
        system_data = data['data']
        
        conn.execute('''
            INSERT INTO monitoring_data 
            (timestamp, server, cpu_usage, ram_usage, disk_usage, gpu_usage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            'localhost',
            system_data['processor']['usage_percent'],
            system_data['memory']['usage_percent'],
            system_data['disk']['usage_percent'],
            system_data.get('gpu', {}).get('usage_percent', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_data(self, hours=24):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT * FROM monitoring_data 
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        '''.format(hours))
        
        data = cursor.fetchall()
        conn.close()
        return data

# Utilisation
db_monitor = DatabaseMonitoring()
client = MonitoringClient(
    uri='ws://localhost:8765',
    on_message=db_monitor.save_data
)
```

### 3. Monitoring avec Alertes

```python
import smtplib
from email.mime.text import MIMEText
from monitoring_client import MonitoringClient

class AlertMonitoring:
    def __init__(self, email_config):
        self.email_config = email_config
        self.thresholds = {
            'cpu': 80,
            'ram': 85,
            'disk': 90,
            'gpu': 95
        }
        self.alert_history = {}
    
    def handle_data(self, data):
        system_data = data['data']
        
        alerts = []
        
        # Vérifier CPU
        cpu_usage = system_data['processor']['usage_percent']
        if cpu_usage > self.thresholds['cpu']:
            alerts.append(f"CPU élevé: {cpu_usage}%")
        
        # Vérifier RAM
        ram_usage = system_data['memory']['usage_percent']
        if ram_usage > self.thresholds['ram']:
            alerts.append(f"RAM élevée: {ram_usage}%")
        
        # Vérifier Disque
        disk_usage = system_data['disk']['usage_percent']
        if disk_usage > self.thresholds['disk']:
            alerts.append(f"Disque plein: {disk_usage}%")
        
        # Envoyer alertes
        if alerts:
            self.send_email_alert(alerts)
    
    def send_email_alert(self, alerts):
        subject = "🚨 Alerte Monitoring Système"
        body = "\n".join(alerts)
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        
        with smtplib.SMTP(self.email_config['smtp_server']) as server:
            server.starttls()
            server.login(self.email_config['username'], 
                        self.email_config['password'])
            server.send_message(msg)

# Configuration
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'username': 'votre-email@gmail.com',
    'password': 'votre-mot-de-passe',
    'from': 'votre-email@gmail.com',
    'to': 'admin@example.com'
}

alert_monitor = AlertMonitoring(email_config)
client = MonitoringClient(
    uri='ws://localhost:8765',
    on_message=alert_monitor.handle_data
)
```

---

## WebSocket Client de Bas Niveau

Le système utilise une classe `WebSocketClient` de bas niveau qui fournit un contrôle granulaire sur la connexion WebSocket.

### Utilisation Directe

```python
from websocket_client import WebSocketClient, ClientState

client = WebSocketClient('ws://localhost:8765')

# Ajouter des gestionnaires d'événements
client.on('monitoring_data', handle_monitoring)
client.on('state_change', handle_state_change)
client.on('*', handle_all_events)  # Gestionnaire universel

# Démarrer la connexion
await client.start()

# Vérifier l'état
if client.state == ClientState.CONNECTED:
    print("Connecté avec succès")

# Arrêter
await client.stop()
```

### Méthodes Principales

```python
# Gestion des événements
client.on(event_type: str, handler: Callable)
client.off(event_type: str, handler: Callable)
client.emit(event_type: str, data: Any)

# Contrôle de connexion
await client.start()
await client.stop()
await client.reconnect()

# État et statistiques
client.state  # ClientState enum
client.is_connected()  # bool
client.get_statistics()  # Dict avec métriques détaillées
```

---

## Système d'Événements

Le client utilise un système d'événements flexible pour gérer les différents types de messages.

### Types d'Événements

| Événement | Description | Données |
|-----------|-------------|----------|
| `monitoring_data` | Données de monitoring | `Dict` avec métriques système |
| `connection_message` | Messages de connexion | `str` message |
| `error_message` | Messages d'erreur | `str` erreur |
| `state_change` | Changement d'état | `{old_state, new_state}` |
| `*` | Tous les événements | Données variables selon l'événement |

### Gestionnaire d'Événements

```python
from websocket_client import WebSocketClient

def handle_monitoring_data(data):
    """Gestionnaire pour données de monitoring"""
    print(f"CPU: {data['data']['processor']['usage_percent']}%")

def handle_state_change(event_data):
    """Gestionnaire pour changements d'état"""
    old_state = event_data['old_state']
    new_state = event_data['new_state']
    print(f"État: {old_state} → {new_state}")

def handle_all_events(event_type, data):
    """Gestionnaire universel"""
    print(f"Événement: {event_type}")

client = WebSocketClient('ws://localhost:8765')

# Enregistrer des gestionnaires personnalisés via le WebSocketClient
client.ws_client.on('monitoring_data', handle_monitoring_data)
client.ws_client.on('state_change', handle_state_change)
client.ws_client.on('*', handle_all_events)

# Supprimer un gestionnaire
client.ws_client.remove_handler('monitoring_data', handle_monitoring_data)
```

### Gestionnaires Asynchrones

```python
async def async_data_handler(data):
    """Gestionnaire asynchrone"""
    # Traitement asynchrone
    await process_data_async(data)
    
    # Sauvegarde en base de données
    await save_to_database(data)

# Le système détecte automatiquement les fonctions async
client.ws_client.on('monitoring_data', async_data_handler)
```

---

## Gestion des États

Le client utilise une machine à états pour gérer les connexions WebSocket.

### États de Connexion

```python
from websocket_client import ClientState

# États disponibles
ClientState.DISCONNECTED    # Déconnecté
ClientState.CONNECTING      # En cours de connexion
ClientState.CONNECTED       # Connecté
ClientState.RECONNECTING    # En cours de reconnexion
ClientState.ERROR          # Erreur de connexion
```

### Surveillance des États

```python
def monitor_connection_state(client):
    """Surveille l'état de la connexion"""
    
    def on_state_change(event_data):
        old_state = event_data['old_state']
        new_state = event_data['new_state']
        
        print(f"Transition: {old_state.name} → {new_state.name}")
        
        # Actions selon l'état
        if new_state == ClientState.CONNECTED:
            print("✅ Connexion établie")
        elif new_state == ClientState.RECONNECTING:
            print("🔄 Reconnexion en cours...")
        elif new_state == ClientState.ERROR:
            print("❌ Erreur de connexion")
    
    client.ws_client.on('state_change', on_state_change)

# Utilisation
client = WebSocketClient('ws://localhost:8765')
monitor_connection_state(client)
```

### Transitions d'États

```
DISCONNECTED → CONNECTING → CONNECTED
     ↑              ↓           ↓
     └─── ERROR ←────┴─── RECONNECTING
```

---

## Statistiques Détaillées

Le système collecte des statistiques détaillées sur les performances et la connectivité.

### Structure des Statistiques

```python
stats = client.get_statistics()

# Structure complète
{
    # Compteurs de messages
    "messages_received": 1250,
    "messages_sent": 45,
    "bytes_received": 2048576,
    "bytes_sent": 8192,
    
    # Informations de connexion
    "connection_start": "2024-01-15T14:30:25.123456",
    "uptime_seconds": 3600.0,
    "reconnect_attempts": 2,
    "total_disconnections": 1,
    
    # État actuel
    "current_state": "connected",
    "last_error": None,
    "error_count": 0,
    
    # Historique des erreurs (5 dernières)
    "error_history": [
        {
            "timestamp": "2024-01-15T14:25:10.123456",
            "error": "Connection timeout",
            "type": "TimeoutError"
        }
    ]
}
```

### Monitoring des Statistiques

```python
import time
from websocket_client import WebSocketClient

def monitor_performance(client):
    """Surveillance des performances en temps réel"""
    
    while client.is_connected():
        stats = client.get_statistics()
        
        # Alertes de performance
        if stats['reconnect_attempts'] > 3:
            print(f"⚠️  Nombreuses reconnexions: {stats['reconnect_attempts']}")
        
        # Rapport périodique
        print(f"📊 Messages: {stats['messages_received']}, "
              f"Reconnexions: {stats['reconnect_attempts']}, "
              f"Uptime: {stats['uptime_seconds']}s")
        
        time.sleep(30)  # Rapport toutes les 30 secondes

# Utilisation
client = WebSocketClient('ws://localhost:8765')
monitor_performance(client)
```

---

## Considérations de Performance

### Gestion de la Mémoire

```python
# Activer l'historique (taille par défaut dans le gestionnaire)
client = MonitoringClient(
    store_history=True
)

# Désactiver l'historique si non nécessaire
client = MonitoringClient(
    store_history=False  # Économise la mémoire
)
```

### Optimisation des Callbacks

```python
# Callback rapide - éviter les opérations lourdes
def fast_callback(data):
    # Traitement minimal
    cpu = data['data']['processor']['usage_percent']
    if cpu > 90:
        send_alert(cpu)  # Opération rapide

# Callback lourd - utiliser threading
import threading

def heavy_callback(data):
    # Déléguer le traitement lourd à un thread
    thread = threading.Thread(
        target=process_heavy_data,
        args=(data,)
    )
    thread.start()

# Callback asynchrone pour opérations I/O
async def async_callback(data):
    # Opérations I/O non-bloquantes
    await save_to_database(data)
    await send_to_api(data)
```

### Réglages Réseau

```python
# Optimisation pour connexions lentes
client = MonitoringClient(
    ping_interval=60.0,        # Ping moins fréquent
    reconnect_interval=15.0,   # Reconnexion plus lente
    operation_timeout=10.0     # Timeout plus long
)

# Optimisation pour connexions rapides
client = MonitoringClient(
    ping_interval=10.0,        # Ping plus fréquent
    reconnect_interval=2.0,    # Reconnexion rapide
    operation_timeout=3.0      # Timeout court
)
```

### Mode Threading

```python
# Mode synchrone utilise un thread dédié
client = MonitoringClient(sync_mode=True)

# Le client crée automatiquement:
# - Un thread pour l'event loop asyncio
# - Synchronisation thread-safe des données
# - Callbacks exécutés dans le thread principal

# Considérations:
# ✅ Simple à utiliser
# ⚠️  Overhead de threading
# ⚠️  Callbacks bloquants affectent les performances
```

---

## API de Référence

### Classe WebSocketClient (Bas Niveau)

```python
class WebSocketClient:
    def __init__(
        self,
        uri: str,
        logger: Optional[logging.Logger] = None,
        reconnect: bool = True,
        reconnect_interval: float = 5.0,
        max_reconnect_attempts: Optional[int] = None,
        ping_interval: float = 30.0,
        ping_timeout: float = 10.0
    ):
        """
        Client WebSocket de bas niveau.
        
        Args:
            uri: URI WebSocket du serveur
            logger: Logger personnalisé
            reconnect: Activer la reconnexion automatique
            reconnect_interval: Intervalle de reconnexion (secondes)
            max_reconnect_attempts: Nombre max de tentatives (None = illimité)
            ping_interval: Intervalle de ping (secondes)
            ping_timeout: Timeout pour les pings (secondes)
        """

    # Méthodes de gestion des gestionnaires (WebSocketClient)
    def on(self, event_type: str, handler: Callable) -> None:
        """Ajoute un gestionnaire d'événement.
        
        Args:
            event_type: Type d'événement ('monitoring_data', 'error_message', '*' pour tous)
            handler: Fonction de rappel (callback) appelée lors de la réception de l'événement
                    La signature dépend du type d'événement :
                    - 'monitoring_data': handler(data: Dict[str, Any])
                    - 'error_message': handler(error: str)
                    - '*': handler(event_type: str, data: Any)
        
        Example:
            def handle_monitoring(data):
                cpu = data['data']['processor']['usage_percent']
                print(f"CPU: {cpu}%")
            
            client.on('monitoring_data', handle_monitoring)
        """
    
    def remove_handler(self, event_type: str, handler: Callable) -> None:
        """Supprime un gestionnaire d'événement spécifique.
        
        Args:
            event_type: Type d'événement déjà enregistré
            handler: Référence exacte à la fonction de rappel à supprimer
        
        Note:
            La référence doit être identique à celle utilisée lors de l'ajout.
            Les fonctions lambda ne peuvent pas être supprimées facilement.
        """
    
    # Méthodes de contrôle
    async def start(self) -> None:
        """Démarre la connexion WebSocket"""
    
    async def stop(self) -> None:
        """Arrête la connexion WebSocket"""
    
    async def reconnect(self) -> None:
        """Force une reconnexion"""
    
    # Propriétés d'état
    @property
    def state(self) -> ClientState:
        """Retourne l'état actuel de la connexion"""
    
    def is_connected(self) -> bool:
        """Vérifie si la connexion est active"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques détaillées"""
```

### Enum ClientState

```python
from enum import Enum

class ClientState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
```

### Classe MonitoringClient

```python
from typing import Union
from pathlib import Path

class MonitoringClient:
    def __init__(
        self,
        uri: str = 'ws://localhost:8765',
        format_type: str = 'simple',
        color: bool = True,
        reconnect: bool = True,
        reconnect_interval: float = 5.0,
        max_reconnect_attempts: Optional[int] = None,
        ping_interval: float = 30.0,
        save_data: Optional[Union[str, Path]] = None,
        store_history: bool = False,
        sync_mode: bool = False,
        logger: Optional[logging.Logger] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_connect: Optional[Callable] = None,
        on_disconnect: Optional[Callable] = None
    ):
        """
        Initialise le client de monitoring.
        
        Args:
            uri: URI WebSocket du serveur
            format_type: Type de format ('simple', 'detailed', 'compact', 'json')
            color: Activer les couleurs
            reconnect: Activer la reconnexion automatique
            reconnect_interval: Intervalle de reconnexion (secondes)
            max_reconnect_attempts: Nombre max de tentatives (None = illimité)
            ping_interval: Intervalle de ping (secondes)
            save_data: Chemin du fichier de sauvegarde (str ou Path)
            store_history: Stocker l'historique en mémoire
            sync_mode: Mode synchrone pour environnements non-async
            logger: Logger personnalisé
            on_message: Callback pour les messages de monitoring
            on_error: Callback pour les erreurs
            on_connect: Callback lors de la connexion
            on_disconnect: Callback lors de la déconnexion
        """
```

#### Méthodes Principales

```python
# Méthodes de contrôle
async def start_async(self) -> None:
    """Démarre le client en mode asynchrone.
    
    Lance la connexion WebSocket et commence à recevoir les messages.
    Cette méthode est non-bloquante et retourne immédiatement.
    Le client continue de fonctionner en arrière-plan jusqu'à stop_async().
    
    Raises:
        websockets.exceptions.ConnectionClosed: Si impossible de se connecter
        asyncio.TimeoutError: Si la connexion prend trop de temps
    """

def start(self) -> None:
    """Démarre le client en mode synchrone.
    
    Crée un thread dédié avec une boucle d'événements asyncio pour gérer
    la connexion WebSocket. Les fonctions de rappel sont exécutées dans
    le thread principal pour maintenir la compatibilité avec le code synchrone.
    
    Note:
        Utilise sync_mode=True automatiquement. Idéal pour intégration
        dans des applications non-asynchrones.
    """

async def stop_async(self) -> None:
    """Arrête le client en mode asynchrone"""

def stop(self) -> None:
    """Arrête le client en mode synchrone"""

# Méthodes de configuration
def set_formatter(self, format_type: str, color: bool = True) -> None:
    """Change le formateur de sortie dynamiquement.
    
    Permet de modifier le format d'affichage pendant l'exécution
    sans redémarrer le client. Utile pour adapter l'affichage
    selon le contexte (debug, production, etc.).
    
    Args:
        format_type: Type de formateur ('simple', 'detailed', 'compact', 'json')
        color: Activer/désactiver les couleurs
    
    Raises:
        ValueError: Si format_type n'est pas supporté
    
    Example:
        # Passer en mode debug avec format détaillé
        client.set_formatter('detailed', color=True)
        
        # Passer en mode production avec JSON
        client.set_formatter('json', color=False)
    """

# Méthodes de données
def get_statistics(self) -> Dict[str, Any]:
    """Retourne les statistiques détaillées du client.
    
    Returns:
        Dictionnaire contenant :
        - messages_received/sent: Compteurs de messages
        - bytes_received/sent: Volume de données transférées
        - uptime_seconds: Durée de connexion en secondes
        - reconnect_attempts: Nombre de tentatives de reconnexion
        - current_state: État actuel de la connexion
        - error_count: Nombre total d'erreurs
        - error_history: Liste des 5 dernières erreurs avec timestamps
    
    Example:
        stats = client.get_statistics()
        print(f"Reçu {stats['messages_received']} messages")
        print(f"Connecté depuis {stats['uptime_seconds']:.1f}s")
    """

def get_history(self) -> List[Dict[str, Any]]:
    """Retourne l'historique des messages reçus.
    
    Returns:
        Liste des messages dans l'ordre chronologique.
        Chaque message contient timestamp, type, et données.
        Limité par MAX_HISTORY_SIZE (1000 par défaut).
    
    Note:
        Disponible uniquement si store_history=True au démarrage.
        Les anciens messages sont automatiquement supprimés quand
        la limite est atteinte (FIFO - First In, First Out).
    
    Raises:
        ValueError: Si l'historique n'est pas activé
    """

def get_last_data(self) -> Optional[Dict[str, Any]]:
    """Retourne les dernières données de monitoring reçues.
    
    Returns:
        Les dernières données de monitoring ou None si aucune reçue.
        Structure typique :
        {
            'timestamp': '2025-01-03T14:30:25.123456',
            'type': 'monitoring_data',
            'data': {
                'processor': {'usage_percent': 45.2},
                'memory': {'usage_percent': 62.8},
                'disk': {'usage_percent': 28.5}
            }
        }
    
    Note:
        Mise à jour automatiquement à chaque nouveau message de monitoring.
        Accessible même si store_history=False.
    """

# Méthodes d'envoi
async def send_async(self, data: Dict[str, Any]) -> None:
    """Envoie des données vers le serveur WebSocket de manière asynchrone.
    
    Args:
        data: Dictionnaire de données à envoyer, sera sérialisé en JSON
    
    Raises:
        websockets.exceptions.ConnectionClosed: Si la connexion est fermée
        json.JSONEncodeError: Si les données ne sont pas sérialisables en JSON
        asyncio.TimeoutError: Si l'envoi dépasse le timeout configuré
    
    Example:
        await client.send_async({
            'action': 'ping',
            'timestamp': time.time()
        })
    """

def send(self, data: Dict[str, Any]) -> None:
    """Envoie des données vers le serveur WebSocket de manière synchrone.
    
    Encapsule send_async() pour utilisation dans du code synchrone.
    Bloque jusqu'à ce que l'envoi soit terminé ou qu'une erreur survienne.
    
    Args:
        data: Dictionnaire de données à envoyer
    
    Raises:
        RuntimeError: Si appelé depuis un contexte asynchrone existant
        Toutes les exceptions de send_async()
    """

# Méthodes de gestionnaires
# Accès aux gestionnaires intégrés
@property
def monitoring_handler(self) -> MonitoringHandler:
    """Accès au gestionnaire de données de monitoring.
    
    Le MonitoringHandler traite automatiquement les messages de type
    'monitoring_data', applique le formatage et gère l'historique.
    
    Returns:
        Instance du gestionnaire créé automatiquement au démarrage
    
    Example:
        # Accéder aux dernières données formatées
        handler = client.monitoring_handler
        if handler.last_data:
            print(f"Dernier CPU: {handler.last_data['data']['processor']['usage_percent']}%")
    """

@property 
def logging_handler(self) -> Optional[LoggingHandler]:
    """Accès au gestionnaire de logging automatique.
    
    Créé automatiquement si save_data est spécifié lors de l'initialisation.
    Gère la sauvegarde de tous les messages avec rotation automatique.
    
    Returns:
        Instance du LoggingHandler ou None si save_data n'est pas configuré
    
    Example:
        if client.logging_handler:
            stats = client.logging_handler.get_stats()
            print(f"Fichier: {stats['log_file']}")
            print(f"Messages sauvegardés: {stats['message_count']}")
    """

# Accès au client de bas niveau
@property
def ws_client(self) -> WebSocketClient:
    """Accès au client WebSocket de bas niveau.
    
    Fournit un accès direct aux fonctionnalités avancées :
    - Gestionnaires d'événements personnalisés
    - Statistiques détaillées de connexion
    - Contrôle granulaire de la connexion
    
    Returns:
        Instance du WebSocketClient utilisé en interne
    
    Warning:
        Utilisation avancée uniquement. Modifications directes
        peuvent affecter le bon fonctionnement du MonitoringClient.
    
    Example:
        # Ajouter un gestionnaire d'événement personnalisé
        client.ws_client.on('custom_event', my_handler)
        
        # Accéder aux statistiques de bas niveau
        print(f"État: {client.ws_client.state.value}")
    """

# Gestionnaires de bas niveau (via ws_client)
def add_custom_handler(self, message_type: str, handler: Callable) -> None:
    """Ajoute un gestionnaire personnalisé via le WebSocketClient"""
    self.ws_client.on(message_type, handler)
```

### Classe SimpleMonitoringClient

```python
class SimpleMonitoringClient:
    def __init__(
        self,
        uri: str = 'ws://localhost:8765',
        on_data: Optional[Callable] = None,
        auto_print: bool = True,
        format_type: str = 'simple'
    ):
        """
        Client simplifié pour un usage basique.
        
        Args:
            uri: URI WebSocket du serveur
            on_data: Callback pour les données
            auto_print: Affichage automatique
            format_type: Type de format de sortie
        """

    def connect(self) -> None:
        """Se connecte au serveur"""

    def disconnect(self) -> None:
        """Se déconnecte du serveur"""

    def wait(self, duration: float) -> None:
        """Attend pendant la durée spécifiée"""

    def is_connected(self) -> bool:
        """Vérifie si connecté"""
```

### Formateurs

#### BaseFormatter

```python
from abc import ABC, abstractmethod

class BaseFormatter(ABC):
    @abstractmethod
    def format_monitoring_data(self, data: Dict[str, Any]) -> str:
        """Formate les données de monitoring"""

    def format_connection_message(self, message: str) -> str:
        """Formate un message de connexion"""

    def format_error(self, error: str) -> str:
        """Formate un message d'erreur"""

    def format_statistics(self, stats: Dict[str, Any]) -> str:
        """Formate les statistiques"""
        
    # Méthodes utilitaires disponibles (privées)
    def _format_bytes(self, bytes_value: int) -> str:
        """Formate une taille en octets"""
        
    def _format_duration(self, seconds: float) -> str:
        """Formate une durée en secondes"""
        
    def _get_usage_color(self, percentage: float, use_color: bool) -> str:
        """Retourne la couleur ANSI selon le pourcentage d'usage"""
```

### Gestionnaires

Les gestionnaires sont des classes simples qui implémentent la méthode `handle_message()` :

```python
class CustomHandler:
    def handle_message(self, message: Dict[str, Any]) -> None:
        """Traite un message reçu"""
        # Votre logique de traitement ici
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Optionnel : retourne les statistiques du gestionnaire"""
        return {}
```

---

## Protocole de Communication

### Format des Messages

Le client s'attend à recevoir des messages JSON du serveur WebSocket avec la structure suivante :

#### Message de Données de Monitoring
```json
{
  "timestamp": "2025-01-03T14:30:25.123456",
  "type": "monitoring_data",
  "data": {
    "processor": {
      "usage_percent": 45.2,
      "temperature": 65.0,
      "frequency_mhz": 2400
    },
    "memory": {
      "usage_percent": 62.8,
      "used_gb": 8.2,
      "total_gb": 13.1,
      "available_gb": 4.9
    },
    "disk": {
      "usage_percent": 28.5,
      "used_gb": 142.5,
      "total_gb": 500.0,
      "free_gb": 357.5
    },
    "gpu": {
      "usage_percent": 15.0,
      "memory_percent": 45.0,
      "temperature": 52.0,
      "memory_used_mb": 2048,
      "memory_total_mb": 4096
    }
  }
}
```

#### Message de Connexion
```json
{
  "timestamp": "2025-01-03T14:30:25.123456",
  "type": "connection_message",
  "message": "Connexion établie avec succès"
}
```

#### Message d'Erreur
```json
{
  "timestamp": "2025-01-03T14:30:25.123456",
  "type": "error_message",
  "error": "Erreur de collecte des données CPU",
  "severity": "warning"
}
```

### Types de Messages Supportés

| Type | Description | Gestionnaire |
|------|-------------|--------------|
| `monitoring_data` | Données de métriques système | MonitoringHandler |
| `connection_message` | Messages informatifs de connexion | Affichage direct |
| `error_message` | Messages d'erreur du serveur | Logging + affichage |
| `ping` / `pong` | Messages de maintien de connexion | Géré automatiquement |

---

## Considérations de Sécurité

### Connexions Sécurisées

Pour des connexions sécurisées, utilisez le protocole `wss://` :

```python
# Connexion sécurisée avec SSL/TLS
client = MonitoringClient(
    uri='wss://monitoring.example.com:8765',
    # SSL sera géré automatiquement
)
```

### Authentification

Le client supporte l'authentification via en-têtes personnalisés :

```python
import websockets

# Configuration des en-têtes d'authentification
extra_headers = {
    'Authorization': 'Bearer your-token-here',
    'X-API-Key': 'your-api-key'
}

# Note: Configuration avancée via WebSocketClient
# (fonctionnalité nécessitant modification du code source)
```

### Protection des Données

- **Logs** : Les fichiers de log peuvent contenir des données sensibles
- **Mémoire** : L'historique stocke les données en mémoire (chiffrement recommandé pour données sensibles)
- **Réseau** : Utilisez WSS en production pour chiffrement des communications

---

## Bonnes Pratiques

### Gestion des Erreurs Robuste

```python
import asyncio
from monitoring_client import MonitoringClient

async def monitoring_robuste():
    """Exemple de surveillance robuste avec gestion d'erreurs complète"""
    
    max_retries = 3
    retry_delay = 5.0
    
    for attempt in range(max_retries):
        try:
            async with MonitoringClient(
                uri='ws://localhost:8765',
                reconnect=True,
                max_reconnect_attempts=10,
                ping_interval=30.0
            ) as client:
                
                # Surveillance continue
                while True:
                    # Vérifier la connexion périodiquement
                    if not client.is_connected():
                        print("⚠️ Connexion perdue, attente de la reconnexion...")
                        await asyncio.sleep(1)
                        continue
                    
                    # Attendre avant la prochaine vérification
                    await asyncio.sleep(10)
                    
        except KeyboardInterrupt:
            print("🛑 Arrêt demandé par l'utilisateur")
            break
            
        except Exception as e:
            print(f"❌ Erreur (tentative {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Nouvelle tentative dans {retry_delay} secondes...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Backoff exponentiel
            else:
                print("💥 Échec définitif après toutes les tentatives")
                raise

# Exécution
asyncio.run(monitoring_robuste())
```

### Optimisation des Performances

```python
# Configuration optimisée pour haute fréquence
client = MonitoringClient(
    uri='ws://localhost:8765',
    store_history=False,        # Économise la mémoire
    ping_interval=60.0,         # Pings moins fréquents
    reconnect_interval=2.0,     # Reconnexion rapide
    format_type='json',         # Format le plus rapide
    color=False                 # Pas de traitement couleur
)

# Callback optimisé
def callback_rapide(data):
    """Callback optimisé pour traitement haute fréquence"""
    # Traitement minimal - déléguer le travail lourd
    if data['data']['processor']['usage_percent'] > 90:
        # Alerte critique immédiate
        print("🚨 CPU CRITIQUE!")
    
    # Traitement lourd en arrière-plan (optionnel)
    # threading.Thread(target=traitement_lourd, args=(data,)).start()

client = MonitoringClient(on_message=callback_rapide)
```

### Intégration dans Applications Existantes

```python
class MonitoringService:
    """Service de monitoring intégrable dans une application existante"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.running = False
        
    async def start(self):
        """Démarre le service de monitoring"""
        if self.running:
            return
            
        self.client = MonitoringClient(
            uri=self.config['uri'],
            on_message=self._handle_data,
            on_error=self._handle_error,
            on_connect=self._on_connect,
            on_disconnect=self._on_disconnect
        )
        
        await self.client.start_async()
        self.running = True
        
    async def stop(self):
        """Arrête proprement le service"""
        if not self.running:
            return
            
        await self.client.stop_async()
        self.running = False
        
    def _handle_data(self, data):
        """Traite les données reçues"""
        # Intégrer avec votre logique métier
        self.config['on_data_callback'](data)
        
    def _handle_error(self, error):
        """Gère les erreurs"""
        print(f"Erreur monitoring: {error}")
        
    def _on_connect(self):
        """Callback de connexion"""
        print("📡 Service de monitoring connecté")
        
    def _on_disconnect(self):
        """Callback de déconnexion"""
        print("📡 Service de monitoring déconnecté")

# Utilisation dans votre application
monitoring = MonitoringService({
    'uri': 'ws://localhost:8765',
    'on_data_callback': your_data_handler
})

# Intégration avec le cycle de vie de l'application
await monitoring.start()
try:
    # Votre application continue de fonctionner
    await your_main_application_loop()
finally:
    await monitoring.stop()
```

---

## Conclusion

Cette documentation couvre tous les aspects du Client de Monitoring WebSocket, depuis l'installation basique jusqu'aux cas d'usage avancés. Le système est conçu pour être à la fois simple à utiliser pour des besoins basiques et suffisamment flexible pour des intégrations complexes.