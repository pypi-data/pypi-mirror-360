# WebSocket Monitoring Client - User Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Command Line Interface](#command-line-interface)
5. [Programmatic Usage](#programmatic-usage)
6. [Output Formats](#output-formats)
7. [Message Handlers](#message-handlers)
8. [Configuration](#configuration)
9. [Logging and Journaling](#logging-and-journaling)
10. [Error Handling](#error-handling)
11. [Advanced Use Cases](#advanced-use-cases)
12. [Low-Level WebSocket Client](#low-level-websocket-client)
13. [Event System](#event-system)
14. [State Management](#state-management)
15. [Detailed Statistics](#detailed-statistics)
16. [Performance Considerations](#performance-considerations)
17. [API Reference](#api-reference)
18. [Communication Protocol](#communication-protocol)
19. [Security Considerations](#security-considerations)
20. [Best Practices](#best-practices)

---

## Introduction

The **WebSocket Monitoring Client** is a professional real-time monitoring system that allows you to receive, process, and display monitoring data via WebSocket. It offers a flexible interface for monitoring system metrics (CPU, RAM, disk, GPU) with support for different output formats and usage modes.

This module was created to work with the module **WebSocket Monitoring Server** : https://pypi.org/project/monitoring-websocket-server/

### Key Features

- ✅ **Robust WebSocket connection** with automatic reconnection
- ✅ **Multiple output formats** (Simple, Detailed, Compact, JSON)
- ✅ **Complete CLI interface** with numerous options
- ✅ **Programmatic API** for integration into your applications
- ✅ **Synchronous and asynchronous modes** according to your needs
- ✅ **Advanced error handling** and complete logging
- ✅ **Data saving** and configurable history
- ✅ **Detailed statistics** of connection and performance
- ✅ **Extensibility** via custom formatters and handlers

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation from PyPI

```bash
pip install monitoring-websocket-client
```

### Installation from Source Code

```bash
git clone https://github.com/nmicinvest/monitoring-websocket-client
cd monitoring-websocket-client
pip install -e .
```

### Entry Points

After installation, the client is accessible via:

```bash
# Direct command (setuptools entry point)
monitoring-websocket-client --help

# Python module execution
python -m monitoring_websocket_system_client --help

# Direct script execution
python cli.py --help
```

### Installation Verification

```bash
monitoring-client --help
```

---

## Quick Start

### 1. Basic Connection

```bash
# Connection to default server (ws://localhost:8765)
monitoring-websocket-client

# Connection to a custom server
monitoring-websocket-client --uri ws://192.168.1.100:8765
```

### 2. Output Formats

```bash
# Simple format (default)
monitoring-websocket-client --format simple

# Detailed format with progress bars
monitoring-websocket-client --format detailed

# Compact format for narrow terminals
monitoring-websocket-client --format compact

# JSON format for integration
monitoring-websocket-client --format json
```

### 3. Data Saving

```bash
# Save all received data
monitoring-websocket-client --save-data monitoring.log

# Run for 60 seconds with statistics
monitoring-websocket-client --duration 60 --stats
```

---

## Command Line Interface

### General Syntax

```bash
monitoring-websocket-client [OPTIONS]
```

### Connection Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `--uri, -u` | WebSocket connection URI | `ws://localhost:8765` |
| `--no-reconnect` | Disable automatic reconnection | Enabled |
| `--reconnect-interval` | Reconnection interval (seconds) | `5.0` |
| `--max-reconnects` | Max number of reconnection attempts | Unlimited |
| `--ping-interval` | Ping interval (seconds) | `30.0` |

### Display Options

| Option | Description | Values |
|--------|-------------|---------|
| `--format, -f` | Output format | `simple`, `detailed`, `compact`, `json` |
| `--no-color` | Disable color output | - |

### Data Options

| Option | Description | Usage |
|--------|-------------|--------|
| `--save-data FILE` | Save to file | `--save-data monitoring.log` |
| `--history` | Store history in memory | - |

### Execution Options

| Option | Description | Usage |
|--------|-------------|--------|
| `--duration, -d` | Execution duration (seconds) | `--duration 60` |
| `--stats, -s` | Display statistics at the end | - |

### Logging Options

| Option | Description | Usage |
|--------|-------------|--------|
| `--verbose, -v` | Enable verbose mode (DEBUG) | - |
| `--log-file` | Custom log file | `--log-file client.log` |

### CLI Usage Examples

#### Basic Monitoring

```bash
# Simple monitoring with colors
monitoring-websocket-client

# Monitoring without colors
monitoring-websocket-client --no-color

# Monitoring with detailed format
monitoring-websocket-client --format detailed
```

#### Monitoring with Saving

```bash
# Save in JSON format
monitoring-websocket-client --format json --save-data data.jsonl

# Save with in-memory history
monitoring-websocket-client --save-data monitoring.log --history
```

#### Timed Monitoring

```bash
# Monitor for 5 minutes
monitoring-websocket-client --duration 300

# Monitor for 1 hour with statistics
monitoring-websocket-client --duration 3600 --stats
```

#### Monitoring with Logging

```bash
# Verbose logging to a file
monitoring-websocket-client --verbose --log-file debug.log

# Normal logging with data saving
monitoring-websocket-client --log-file client.log --save-data monitoring.log
```

#### Remote Server Monitoring

```bash
# Connection to a remote server
monitoring-websocket-client --uri ws://192.168.1.100:8765

# Connection with custom parameters
monitoring-websocket-client --uri ws://server.example.com:9090 \
  --reconnect-interval 10 \
  --max-reconnects 5 \
  --ping-interval 60
```

---

## Programmatic Usage

### Asynchronous Mode

#### Usage with Context Manager

```python
import asyncio
from monitoring_client import MonitoringClient

async def main():
    async with MonitoringClient('ws://localhost:8765') as client:
        # Client connects automatically
        await client.start_async()
        
        # Wait for 60 seconds
        await asyncio.sleep(60)
        
        # Get statistics
        stats = client.get_statistics()
        print(f"Messages received: {stats['messages_received']}")
        
        # Client disconnects automatically

asyncio.run(main())
```

#### Manual Usage

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
        
        # Your logic here
        await asyncio.sleep(120)
        
    finally:
        await client.stop_async()

asyncio.run(main())
```

### Synchronous Mode

#### Usage with Context Manager

```python
from monitoring_client import MonitoringClient
import time

def main():
    with MonitoringClient('ws://localhost:8765', sync_mode=True) as client:
        # Client connects automatically
        client.start()
        
        # Wait for 60 seconds
        time.sleep(60)
        
        # Get statistics
        stats = client.get_statistics()
        print(f"Messages received: {stats['messages_received']}")
        
        # Client disconnects automatically

main()
```

#### Simplified Client

```python
from monitoring_client import SimpleMonitoringClient

def process_data(data):
    """Callback function to process data"""
    cpu_usage = data['data']['processor']['usage_percent']
    print(f"CPU: {cpu_usage}%")
    
    if cpu_usage > 80:
        print("⚠️  Alert: High CPU!")

def main():
    client = SimpleMonitoringClient(
        uri='ws://localhost:8765',
        on_data=process_data,  # Custom callback
        auto_print=False       # Disable automatic display
    )
    
    try:
        client.connect()
        client.wait(60)  # Wait for 60 seconds
    finally:
        client.disconnect()

main()
```

### Custom Callbacks

#### Data Callback

```python
from monitoring_client import MonitoringClient

def handle_monitoring_data(data):
    """Handler for monitoring data"""
    system_data = data['data']
    
    # CPU processing
    cpu_usage = system_data['processor']['usage_percent']
    if cpu_usage > 90:
        send_alert(f"Critical CPU: {cpu_usage}%")
    
    # RAM processing
    ram_usage = system_data['memory']['usage_percent']
    if ram_usage > 85:
        send_alert(f"High RAM: {ram_usage}%")
    
    # Save to database
    save_to_database(system_data)

def handle_connection_event(event_type, message):
    """Handler for connection events"""
    print(f"Connection: {event_type} - {message}")

client = MonitoringClient(
    uri='ws://localhost:8765',
    on_message=handle_monitoring_data,
    on_connection_event=handle_connection_event
)
```

#### Error Callback

```python
from monitoring_client import MonitoringClient

def handle_error(error):
    """Custom error handler"""
    print(f"Error detected: {error}")
    
    # Send notification
    send_notification(f"Monitoring error: {error}")
    
    # Log error
    logger.error(f"Monitoring error: {error}")

client = MonitoringClient(
    uri='ws://localhost:8765',
    on_error=handle_error
)
```

---

## Output Formats

### Simple Format (`simple`)

**Features:**
- Single-line output
- Color coding by usage
- Compact and readable

**Example:**
```
CPU: 45.2% | RAM: 62.8% | Disk: 28.5% | GPU: 15.0%
```

**Configuration:**
```python
client = MonitoringClient(format_type='simple', color=True)
```

### Detailed Format (`detailed`)

**Features:**
- Multi-line output
- Visual progress bars
- Complete system information
- Timestamp

**Example:**
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

### Compact Format (`compact`)

**Features:**
- Ultra-compact for narrow terminals
- Unicode separators
- Essential data only

**Example:**
```
[14:30:25] CPU:45% │ RAM:63%(8.2/13G) │ DSK:29% │ GPU:15%/45%
```

**Configuration:**
```python
client = MonitoringClient(format_type='compact', color=True)
```

### JSON Format (`json`)

**Features:**
- Machine-readable format
- No colors
- Standardized structure
- Perfect for integration

**Example:**
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

## Message Handlers

### MonitoringHandler

**Function:** Processes monitoring data messages

**Features:**
- Data filtering
- History storage
- Last data cache
- Formatted display

**Configuration:**
```python
from handlers import MonitoringHandler

# Handlers are automatically created by MonitoringClient
# For custom control, access existing handlers:
monitoring_handler = client.monitoring_handler
logging_handler = client.logging_handler  # If save_data specified

# Or add custom handlers
client.ws_client.on('monitoring_data', custom_handler)
```

### LoggingHandler

**Function:** Records all messages to files

**Features:**
- Automatic log rotation
- Raw or formatted logging
- Logging statistics
- Configurable naming

**Configuration:**
```python
from handlers import LoggingHandler

# LoggingHandler is automatically created if save_data is specified
client = MonitoringClient(
    save_data='monitoring.log'  # Automatically creates LoggingHandler
)

# Access to created handler
if client.logging_handler:
    stats = client.logging_handler.get_stats()
    print(f"Messages recorded: {stats['message_count']}")
```

### Custom Handler

**Creating a custom handler:**

```python
class AlertHandler:
    def __init__(self, threshold=80):
        self.threshold = threshold
        
    def handle_message(self, message):
        if message['type'] == 'monitoring_data':
            data = message['data']
            
            # Check CPU
            cpu_usage = data['processor']['usage_percent']
            if cpu_usage > self.threshold:
                self.send_alert(f"High CPU: {cpu_usage}%")
            
            # Check RAM
            ram_usage = data['memory']['usage_percent']
            if ram_usage > self.threshold:
                self.send_alert(f"High RAM: {ram_usage}%")
    
    def send_alert(self, message):
        # Your alert logic
        print(f"🚨 ALERT: {message}")

# Usage
alert_handler = AlertHandler(threshold=85)
client.ws_client.on('monitoring_data', alert_handler.handle_message)
```

---

## Configuration

### Configuration File

The system uses the `config.py` file for all configurations:

```python
# Network configuration
DEFAULT_WEBSOCKET_URI = 'ws://localhost:8765'
RECONNECT_INTERVAL = 5.0
PING_INTERVAL = 30.0
PING_TIMEOUT = 10.0
MAX_RECONNECT_ATTEMPTS = None  # Unlimited

# Display configuration
DEFAULT_FORMAT_TYPE = 'simple'
THRESHOLD_WARNING = 80.0
THRESHOLD_CRITICAL = 90.0
PROGRESS_BAR_LENGTH = 20
TIME_FORMAT = '%H:%M:%S'
JSON_INDENT_LEVEL = 2

# Data configuration
MAX_HISTORY_SIZE = 1000
LOG_ROTATION_SIZE = 10 * 1024 * 1024  # 10MB
ERROR_HISTORY_LIMIT = 5

# Performance configuration
OPERATION_TIMEOUT = 5.0
SEND_TIMEOUT = 5.0
CLI_POLLING_INTERVAL = 0.1
```

### Environment Variables

```bash
# WebSocket URI
export MONITORING_WEBSOCKET_URI=ws://monitoring.example.com:8765

# Default format
export MONITORING_FORMAT=detailed

# Log level
export MONITORING_LOG_LEVEL=DEBUG

# Log file
export MONITORING_LOG_FILE=/var/log/monitoring.log
```

### Programmatic Configuration

```python
from monitoring_client import MonitoringClient

# Complete configuration
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

## Logging and Journaling

### Log Levels

| Level | Description | Usage |
|-------|-------------|-------|
| `DEBUG` | Detailed information | Development, debugging |
| `INFO` | General information | Normal operation |
| `WARNING` | Warnings | Potential problems |
| `ERROR` | Errors | Recoverable errors |
| `CRITICAL` | Critical errors | Serious errors |

### Logging Configuration

#### Via CLI

```bash
# Normal logging
monitoring-client --log-file monitoring.log

# Verbose logging
monitoring-client --verbose --log-file debug.log

# Logging with saving
monitoring-client --log-file logs/client.log --save-data data/monitoring.log
```

#### Via Code

```python
import logging
from monitoring_client import MonitoringClient

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('monitoring_client')

# Usage with client
client = MonitoringClient(
    uri='ws://localhost:8765',
    logger=logger
)
```

### Log Rotation

```python
import logging.handlers
from monitoring_client import MonitoringClient

# Logger with rotation
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

## Error Handling

### Error Types

#### Connection Errors

```python
from monitoring_client import MonitoringClient
import websockets.exceptions

try:
    client = MonitoringClient('ws://invalid-server:8765')
    client.start()
except websockets.exceptions.ConnectionClosedError as e:
    print(f"Unable to connect: {e}")
    # Fallback logic
except Exception as e:
    print(f"Connection error: {e}")
```

#### Timeout Errors

```python
from monitoring_client import MonitoringClient
import asyncio

try:
    client = MonitoringClient()
    client.start()
except asyncio.TimeoutError as e:
    print(f"Timeout: {e}")
    # Retry or alternative
except Exception as e:
    print(f"Error: {e}")
```

#### Format Errors

```python
from monitoring_client import MonitoringClient

try:
    client = MonitoringClient(format_type='invalid_format')
except ValueError as e:
    print(f"Invalid format: {e}")
    # Use default format
    client = MonitoringClient(format_type='simple')
except Exception as e:
    print(f"Configuration error: {e}")
```

### Robust Handling

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
                time.sleep(3600)  # Monitor for 1 hour
                
            break  # Success, exit loop
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All attempts failed")
                raise

robust_monitoring()
```

---

## Advanced Use Cases

### 1. Distributed Monitoring

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
            return  # Wait for all data
        
        total_cpu = sum(d['data']['processor']['usage_percent'] 
                       for d in self.data.values())
        avg_cpu = total_cpu / len(self.data)
        
        if avg_cpu > 80:
            self.send_cluster_alert(f"High cluster CPU: {avg_cpu:.1f}%")
    
    def send_cluster_alert(self, message):
        print(f"🚨 CLUSTER ALERT: {message}")

# Usage
monitors = DistributedMonitoring(['server1', 'server2', 'server3'])
asyncio.run(monitors.start_monitoring())
```

### 2. Database Monitoring

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

# Usage
db_monitor = DatabaseMonitoring()
client = MonitoringClient(
    uri='ws://localhost:8765',
    on_message=db_monitor.save_data
)
```

### 3. Alert Monitoring

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
        
        # Check CPU
        cpu_usage = system_data['processor']['usage_percent']
        if cpu_usage > self.thresholds['cpu']:
            alerts.append(f"High CPU: {cpu_usage}%")
        
        # Check RAM
        ram_usage = system_data['memory']['usage_percent']
        if ram_usage > self.thresholds['ram']:
            alerts.append(f"High RAM: {ram_usage}%")
        
        # Check Disk
        disk_usage = system_data['disk']['usage_percent']
        if disk_usage > self.thresholds['disk']:
            alerts.append(f"Disk full: {disk_usage}%")
        
        # Send alerts
        if alerts:
            self.send_email_alert(alerts)
    
    def send_email_alert(self, alerts):
        subject = "🚨 System Monitoring Alert"
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
    'username': 'your-email@gmail.com',
    'password': 'your-password',
    'from': 'your-email@gmail.com',
    'to': 'admin@example.com'
}

alert_monitor = AlertMonitoring(email_config)
client = MonitoringClient(
    uri='ws://localhost:8765',
    on_message=alert_monitor.handle_data
)
```

---

## Low-Level WebSocket Client

The system uses a low-level `WebSocketClient` class that provides granular control over the WebSocket connection.

### Direct Usage

```python
from websocket_client import WebSocketClient, ClientState

client = WebSocketClient('ws://localhost:8765')

# Add event handlers
client.on('monitoring_data', handle_monitoring)
client.on('state_change', handle_state_change)
client.on('*', handle_all_events)  # Universal handler

# Start connection
await client.start()

# Check state
if client.state == ClientState.CONNECTED:
    print("Successfully connected")

# Stop
await client.stop()
```

### Main Methods

```python
# Event management
client.on(event_type: str, handler: Callable)
client.off(event_type: str, handler: Callable)
client.emit(event_type: str, data: Any)

# Connection control
await client.start()
await client.stop()
await client.reconnect()

# State and statistics
client.state  # ClientState enum
client.is_connected()  # bool
client.get_statistics()  # Dict with detailed metrics
```

---

## Event System

The client uses a flexible event system to handle different types of messages.

### Event Types

| Event | Description | Data |
|-------|-------------|------|
| `monitoring_data` | Monitoring data | `Dict` with system metrics |
| `connection_message` | Connection messages | `str` message |
| `error_message` | Error messages | `str` error |
| `state_change` | State change | `{old_state, new_state}` |
| `*` | All events | Variable data depending on event |

### Event Handler

```python
from websocket_client import WebSocketClient

def handle_monitoring_data(data):
    """Handler for monitoring data"""
    print(f"CPU: {data['data']['processor']['usage_percent']}%")

def handle_state_change(event_data):
    """Handler for state changes"""
    old_state = event_data['old_state']
    new_state = event_data['new_state']
    print(f"State: {old_state} → {new_state}")

def handle_all_events(event_type, data):
    """Universal handler"""
    print(f"Event: {event_type}")

client = WebSocketClient('ws://localhost:8765')

# Register custom handlers via WebSocketClient
client.ws_client.on('monitoring_data', handle_monitoring_data)
client.ws_client.on('state_change', handle_state_change)
client.ws_client.on('*', handle_all_events)

# Remove a handler
client.ws_client.remove_handler('monitoring_data', handle_monitoring_data)
```

### Asynchronous Handlers

```python
async def async_data_handler(data):
    """Asynchronous handler"""
    # Asynchronous processing
    await process_data_async(data)
    
    # Save to database
    await save_to_database(data)

# System automatically detects async functions
client.ws_client.on('monitoring_data', async_data_handler)
```

---

## State Management

The client uses a state machine to manage WebSocket connections.

### Connection States

```python
from websocket_client import ClientState

# Available states
ClientState.DISCONNECTED    # Disconnected
ClientState.CONNECTING      # Connecting
ClientState.CONNECTED       # Connected
ClientState.RECONNECTING    # Reconnecting
ClientState.ERROR          # Connection error
```

### State Monitoring

```python
def monitor_connection_state(client):
    """Monitor connection state"""
    
    def on_state_change(event_data):
        old_state = event_data['old_state']
        new_state = event_data['new_state']
        
        print(f"Transition: {old_state.name} → {new_state.name}")
        
        # Actions by state
        if new_state == ClientState.CONNECTED:
            print("✅ Connection established")
        elif new_state == ClientState.RECONNECTING:
            print("🔄 Reconnecting...")
        elif new_state == ClientState.ERROR:
            print("❌ Connection error")
    
    client.ws_client.on('state_change', on_state_change)

# Usage
client = WebSocketClient('ws://localhost:8765')
monitor_connection_state(client)
```

### State Transitions

```
DISCONNECTED → CONNECTING → CONNECTED
     ↑              ↓           ↓
     └─── ERROR ←────┴─── RECONNECTING
```

---

## Detailed Statistics

The system collects detailed statistics on performance and connectivity.

### Statistics Structure

```python
stats = client.get_statistics()

# Complete structure
{
    # Message counters
    "messages_received": 1250,
    "messages_sent": 45,
    "bytes_received": 2048576,
    "bytes_sent": 8192,
    
    # Connection information
    "connection_start": "2024-01-15T14:30:25.123456",
    "uptime_seconds": 3600.0,
    "reconnect_attempts": 2,
    "total_disconnections": 1,
    
    # Current state
    "current_state": "connected",
    "last_error": None,
    "error_count": 0,
    
    # Error history (last 5)
    "error_history": [
        {
            "timestamp": "2024-01-15T14:25:10.123456",
            "error": "Connection timeout",
            "type": "TimeoutError"
        }
    ]
}
```

### Statistics Monitoring

```python
import time
from websocket_client import WebSocketClient

def monitor_performance(client):
    """Real-time performance monitoring"""
    
    while client.is_connected():
        stats = client.get_statistics()
        
        # Performance alerts
        if stats['reconnect_attempts'] > 3:
            print(f"⚠️  Many reconnections: {stats['reconnect_attempts']}")
        
        # Periodic report
        print(f"📊 Messages: {stats['messages_received']}, "
              f"Reconnections: {stats['reconnect_attempts']}, "
              f"Uptime: {stats['uptime_seconds']}s")
        
        time.sleep(30)  # Report every 30 seconds

# Usage
client = WebSocketClient('ws://localhost:8765')
monitor_performance(client)
```

---

## Performance Considerations

### Memory Management

```python
# Enable history (default size in handler)
client = MonitoringClient(
    store_history=True
)

# Disable history if not needed
client = MonitoringClient(
    store_history=False  # Saves memory
)
```

### Callback Optimization

```python
# Fast callback - avoid heavy operations
def fast_callback(data):
    # Minimal processing
    cpu = data['data']['processor']['usage_percent']
    if cpu > 90:
        send_alert(cpu)  # Fast operation

# Heavy callback - use threading
import threading

def heavy_callback(data):
    # Delegate heavy processing to a thread
    thread = threading.Thread(
        target=process_heavy_data,
        args=(data,)
    )
    thread.start()

# Asynchronous callback for I/O operations
async def async_callback(data):
    # Non-blocking I/O operations
    await save_to_database(data)
    await send_to_api(data)
```

### Network Settings

```python
# Optimization for slow connections
client = MonitoringClient(
    ping_interval=60.0,        # Less frequent ping
    reconnect_interval=15.0,   # Slower reconnection
    operation_timeout=10.0     # Longer timeout
)

# Optimization for fast connections
client = MonitoringClient(
    ping_interval=10.0,        # More frequent ping
    reconnect_interval=2.0,    # Fast reconnection
    operation_timeout=3.0      # Short timeout
)
```

### Threading Mode

```python
# Synchronous mode uses a dedicated thread
client = MonitoringClient(sync_mode=True)

# Client automatically creates:
# - A thread for asyncio event loop
# - Thread-safe data synchronization
# - Callbacks executed in main thread

# Considerations:
# ✅ Simple to use
# ⚠️  Threading overhead
# ⚠️  Blocking callbacks affect performance
```

---

## API Reference

### WebSocketClient Class (Low Level)

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
        Low-level WebSocket client.
        
        Args:
            uri: WebSocket server URI
            logger: Custom logger
            reconnect: Enable automatic reconnection
            reconnect_interval: Reconnection interval (seconds)
            max_reconnect_attempts: Max number of attempts (None = unlimited)
            ping_interval: Ping interval (seconds)
            ping_timeout: Ping timeout (seconds)
        """

    # Handler management methods (WebSocketClient)
    def on(self, event_type: str, handler: Callable) -> None:
        """Adds an event handler.
        
        Args:
            event_type: Event type ('monitoring_data', 'error_message', '*' for all)
            handler: Callback function called when event is received
                    Signature depends on event type:
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
        """Removes a specific event handler.
        
        Args:
            event_type: Already registered event type
            handler: Exact reference to callback function to remove
        
        Note:
            Reference must be identical to one used when adding.
            Lambda functions cannot be easily removed.
        """
    
    # Control methods
    async def start(self) -> None:
        """Starts WebSocket connection"""
    
    async def stop(self) -> None:
        """Stops WebSocket connection"""
    
    async def reconnect(self) -> None:
        """Forces a reconnection"""
    
    # State properties
    @property
    def state(self) -> ClientState:
        """Returns current connection state"""
    
    def is_connected(self) -> bool:
        """Checks if connection is active"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Returns detailed statistics"""
```

### ClientState Enum

```python
from enum import Enum

class ClientState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
```

### MonitoringClient Class

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
        Initializes the monitoring client.
        
        Args:
            uri: WebSocket server URI
            format_type: Format type ('simple', 'detailed', 'compact', 'json')
            color: Enable colors
            reconnect: Enable automatic reconnection
            reconnect_interval: Reconnection interval (seconds)
            max_reconnect_attempts: Max number of attempts (None = unlimited)
            ping_interval: Ping interval (seconds)
            save_data: Save file path (str or Path)
            store_history: Store history in memory
            sync_mode: Synchronous mode for non-async environments
            logger: Custom logger
            on_message: Callback for monitoring messages
            on_error: Callback for errors
            on_connect: Callback on connection
            on_disconnect: Callback on disconnection
        """
```

#### Main Methods

```python
# Control methods
async def start_async(self) -> None:
    """Starts client in asynchronous mode.
    
    Launches WebSocket connection and starts receiving messages.
    This method is non-blocking and returns immediately.
    Client continues running in background until stop_async().
    
    Raises:
        websockets.exceptions.ConnectionClosed: If unable to connect
        asyncio.TimeoutError: If connection takes too long
    """

def start(self) -> None:
    """Starts client in synchronous mode.
    
    Creates a dedicated thread with asyncio event loop to manage
    WebSocket connection. Callbacks are executed in main thread
    to maintain compatibility with synchronous code.
    
    Note:
        Automatically uses sync_mode=True. Ideal for integration
        into non-asynchronous applications.
    """

async def stop_async(self) -> None:
    """Stops client in asynchronous mode"""

def stop(self) -> None:
    """Stops client in synchronous mode"""

# Configuration methods
def set_formatter(self, format_type: str, color: bool = True) -> None:
    """Dynamically changes output formatter.
    
    Allows modifying display format during execution
    without restarting client. Useful for adapting display
    to context (debug, production, etc.).
    
    Args:
        format_type: Formatter type ('simple', 'detailed', 'compact', 'json')
        color: Enable/disable colors
    
    Raises:
        ValueError: If format_type is not supported
    
    Example:
        # Switch to debug mode with detailed format
        client.set_formatter('detailed', color=True)
        
        # Switch to production mode with JSON
        client.set_formatter('json', color=False)
    """

# Data methods
def get_statistics(self) -> Dict[str, Any]:
    """Returns detailed client statistics.
    
    Returns:
        Dictionary containing:
        - messages_received/sent: Message counters
        - bytes_received/sent: Data volume transferred
        - uptime_seconds: Connection duration in seconds
        - reconnect_attempts: Number of reconnection attempts
        - current_state: Current connection state
        - error_count: Total error count
        - error_history: List of last 5 errors with timestamps
    
    Example:
        stats = client.get_statistics()
        print(f"Received {stats['messages_received']} messages")
        print(f"Connected for {stats['uptime_seconds']:.1f}s")
    """

def get_history(self) -> List[Dict[str, Any]]:
    """Returns history of received messages.
    
    Returns:
        List of messages in chronological order.
        Each message contains timestamp, type, and data.
        Limited by MAX_HISTORY_SIZE (1000 by default).
    
    Note:
        Only available if store_history=True at startup.
        Old messages are automatically deleted when
        limit is reached (FIFO - First In, First Out).
    
    Raises:
        ValueError: If history is not enabled
    """

def get_last_data(self) -> Optional[Dict[str, Any]]:
    """Returns last monitoring data received.
    
    Returns:
        Last monitoring data or None if none received.
        Typical structure:
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
        Automatically updated with each new monitoring message.
        Accessible even if store_history=False.
    """

# Send methods
async def send_async(self, data: Dict[str, Any]) -> None:
    """Sends data to WebSocket server asynchronously.
    
    Args:
        data: Dictionary of data to send, will be serialized to JSON
    
    Raises:
        websockets.exceptions.ConnectionClosed: If connection is closed
        json.JSONEncodeError: If data cannot be serialized to JSON
        asyncio.TimeoutError: If sending exceeds configured timeout
    
    Example:
        await client.send_async({
            'action': 'ping',
            'timestamp': time.time()
        })
    """

def send(self, data: Dict[str, Any]) -> None:
    """Sends data to WebSocket server synchronously.
    
    Wraps send_async() for use in synchronous code.
    Blocks until sending is complete or error occurs.
    
    Args:
        data: Dictionary of data to send
    
    Raises:
        RuntimeError: If called from existing asynchronous context
        All exceptions from send_async()
    """

# Handler methods
# Access to built-in handlers
@property
def monitoring_handler(self) -> MonitoringHandler:
    """Access to monitoring data handler.
    
    MonitoringHandler automatically processes messages of type
    'monitoring_data', applies formatting and manages history.
    
    Returns:
        Handler instance automatically created at startup
    
    Example:
        # Access last formatted data
        handler = client.monitoring_handler
        if handler.last_data:
            print(f"Last CPU: {handler.last_data['data']['processor']['usage_percent']}%")
    """

@property 
def logging_handler(self) -> Optional[LoggingHandler]:
    """Access to automatic logging handler.
    
    Automatically created if save_data is specified during initialization.
    Manages saving all messages with automatic rotation.
    
    Returns:
        LoggingHandler instance or None if save_data not configured
    
    Example:
        if client.logging_handler:
            stats = client.logging_handler.get_stats()
            print(f"File: {stats['log_file']}")
            print(f"Messages saved: {stats['message_count']}")
    """

# Access to low-level client
@property
def ws_client(self) -> WebSocketClient:
    """Access to low-level WebSocket client.
    
    Provides direct access to advanced features:
    - Custom event handlers
    - Detailed connection statistics
    - Granular connection control
    
    Returns:
        WebSocketClient instance used internally
    
    Warning:
        Advanced usage only. Direct modifications
        may affect proper functioning of MonitoringClient.
    
    Example:
        # Add custom event handler
        client.ws_client.on('custom_event', my_handler)
        
        # Access low-level statistics
        print(f"State: {client.ws_client.state.value}")
    """

# Low-level handlers (via ws_client)
def add_custom_handler(self, message_type: str, handler: Callable) -> None:
    """Adds custom handler via WebSocketClient"""
    self.ws_client.on(message_type, handler)
```

### SimpleMonitoringClient Class

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
        Simplified client for basic usage.
        
        Args:
            uri: WebSocket server URI
            on_data: Callback for data
            auto_print: Automatic display
            format_type: Output format type
        """

    def connect(self) -> None:
        """Connects to server"""

    def disconnect(self) -> None:
        """Disconnects from server"""

    def wait(self, duration: float) -> None:
        """Waits for specified duration"""

    def is_connected(self) -> bool:
        """Checks if connected"""
```

### Formatters

#### BaseFormatter

```python
from abc import ABC, abstractmethod

class BaseFormatter(ABC):
    @abstractmethod
    def format_monitoring_data(self, data: Dict[str, Any]) -> str:
        """Formats monitoring data"""

    def format_connection_message(self, message: str) -> str:
        """Formats a connection message"""

    def format_error(self, error: str) -> str:
        """Formats an error message"""

    def format_statistics(self, stats: Dict[str, Any]) -> str:
        """Formats statistics"""
        
    # Available utility methods (private)
    def _format_bytes(self, bytes_value: int) -> str:
        """Formats size in bytes"""
        
    def _format_duration(self, seconds: float) -> str:
        """Formats duration in seconds"""
        
    def _get_usage_color(self, percentage: float, use_color: bool) -> str:
        """Returns ANSI color based on usage percentage"""
```

### Handlers

Handlers are simple classes that implement the `handle_message()` method:

```python
class CustomHandler:
    def handle_message(self, message: Dict[str, Any]) -> None:
        """Processes a received message"""
        # Your processing logic here
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Optional: returns handler statistics"""
        return {}
```

---

## Communication Protocol

### Message Format

The client expects to receive JSON messages from the WebSocket server with the following structure:

#### Monitoring Data Message
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

#### Connection Message
```json
{
  "timestamp": "2025-01-03T14:30:25.123456",
  "type": "connection_message",
  "message": "Connection established successfully"
}
```

#### Error Message
```json
{
  "timestamp": "2025-01-03T14:30:25.123456",
  "type": "error_message",
  "error": "CPU data collection error",
  "severity": "warning"
}
```

### Supported Message Types

| Type | Description | Handler |
|------|-------------|---------|
| `monitoring_data` | System metrics data | MonitoringHandler |
| `connection_message` | Connection informational messages | Direct display |
| `error_message` | Server error messages | Logging + display |
| `ping` / `pong` | Connection maintenance messages | Handled automatically |

---

## Security Considerations

### Secure Connections

For secure connections, use the `wss://` protocol:

```python
# Secure connection with SSL/TLS
client = MonitoringClient(
    uri='wss://monitoring.example.com:8765',
    # SSL will be handled automatically
)
```

### Authentication

The client supports authentication via custom headers:

```python
import websockets

# Authentication headers configuration
extra_headers = {
    'Authorization': 'Bearer your-token-here',
    'X-API-Key': 'your-api-key'
}

# Note: Advanced configuration via WebSocketClient
# (feature requiring source code modification)
```

### Data Protection

- **Logs**: Log files may contain sensitive data
- **Memory**: History stores data in memory (encryption recommended for sensitive data)
- **Network**: Use WSS in production for communication encryption

---

## Best Practices

### Robust Error Handling

```python
import asyncio
from monitoring_client import MonitoringClient

async def robust_monitoring():
    """Example of robust monitoring with complete error handling"""
    
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
                
                # Continuous monitoring
                while True:
                    # Check connection periodically
                    if not client.is_connected():
                        print("⚠️ Connection lost, waiting for reconnection...")
                        await asyncio.sleep(1)
                        continue
                    
                    # Wait before next check
                    await asyncio.sleep(10)
                    
        except KeyboardInterrupt:
            print("🛑 Stop requested by user")
            break
            
        except Exception as e:
            print(f"❌ Error (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("💥 Definitive failure after all attempts")
                raise

# Execution
asyncio.run(robust_monitoring())
```

### Performance Optimization

```python
# Optimized configuration for high frequency
client = MonitoringClient(
    uri='ws://localhost:8765',
    store_history=False,        # Save memory
    ping_interval=60.0,         # Less frequent pings
    reconnect_interval=2.0,     # Fast reconnection
    format_type='json',         # Fastest format
    color=False                 # No color processing
)

# Optimized callback
def fast_callback(data):
    """Optimized callback for high frequency processing"""
    # Minimal processing - delegate heavy work
    if data['data']['processor']['usage_percent'] > 90:
        # Immediate critical alert
        print("🚨 CRITICAL CPU!")
    
    # Heavy processing in background (optional)
    # threading.Thread(target=heavy_processing, args=(data,)).start()

client = MonitoringClient(on_message=fast_callback)
```

### Integration into Existing Applications

```python
class MonitoringService:
    """Monitoring service integrable into existing application"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.running = False
        
    async def start(self):
        """Starts monitoring service"""
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
        """Properly stops service"""
        if not self.running:
            return
            
        await self.client.stop_async()
        self.running = False
        
    def _handle_data(self, data):
        """Processes received data"""
        # Integrate with your business logic
        self.config['on_data_callback'](data)
        
    def _handle_error(self, error):
        """Handles errors"""
        print(f"Monitoring error: {error}")
        
    def _on_connect(self):
        """Connection callback"""
        print("📡 Monitoring service connected")
        
    def _on_disconnect(self):
        """Disconnection callback"""
        print("📡 Monitoring service disconnected")

# Usage in your application
monitoring = MonitoringService({
    'uri': 'ws://localhost:8765',
    'on_data_callback': your_data_handler
})

# Integration with application lifecycle
await monitoring.start()
try:
    # Your application continues running
    await your_main_application_loop()
finally:
    await monitoring.stop()
```

---

## Conclusion

This documentation covers all aspects of the WebSocket Monitoring Client, from basic installation to advanced use cases. The system is designed to be both simple to use for basic needs and flexible enough for complex integrations.