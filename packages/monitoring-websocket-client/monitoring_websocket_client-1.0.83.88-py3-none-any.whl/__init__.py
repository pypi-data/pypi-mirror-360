"""
Client de monitoring WebSocket professionnel.

Ce package fournit un client WebSocket complet pour le monitoring de système
en temps réel, avec support pour différents formats d'affichage, gestion
automatique de la reconnexion, et API synchrone/asynchrone flexible.

Classes principales:
    - WebSocketClient: Client WebSocket de base avec reconnexion automatique
    - MonitoringClient: Client de haut niveau avec formatage intégré
    - SimpleMonitoringClient: Client simplifié pour usage synchrone

Formateurs disponibles:
    - SimpleFormatter: Affichage minimaliste
    - DetailedFormatter: Affichage détaillé avec barres de progression
    - CompactFormatter: Format compact pour espaces restreints
    - JsonFormatter: Sortie JSON pour intégration
"""

from .websocket_client import WebSocketClient, ClientState, ClientStatistics
from .formatters import (
    BaseFormatter,
    SimpleFormatter,
    DetailedFormatter,
    JsonFormatter,
    CompactFormatter
)
from .handlers import MonitoringHandler, LoggingHandler
from .monitoring_client import MonitoringClient, SimpleMonitoringClient

__all__ = [
    'WebSocketClient',
    'ClientState', 
    'ClientStatistics',
    'BaseFormatter',
    'SimpleFormatter',
    'DetailedFormatter',
    'JsonFormatter',
    'CompactFormatter',
    'MonitoringHandler',
    'LoggingHandler',
    'MonitoringClient',
    'SimpleMonitoringClient'
]