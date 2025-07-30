"""
Client WebSocket professionnel pour le système de monitoring.

Ce module implémente un client WebSocket robuste avec gestion automatique de la reconnexion,
suivi des statistiques, gestion des états et support des gestionnaires de messages.
Il fournit une base solide pour construire des clients de monitoring temps réel.
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
import websockets
from websockets.exceptions import WebSocketException, ConnectionClosed

from config import (
    RECONNECT_INTERVAL,
    PING_INTERVAL,
    PING_TIMEOUT,
    ERROR_HISTORY_LIMIT,
    DEFAULT_ENCODING
)


class ClientState(Enum):
    """États de connexion du client.
    
    Cette énumération définit tous les états possibles du client WebSocket
    pour un suivi précis de la connexion.
    """
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class ClientStatistics:
    """Suivi des statistiques du client.
    
    Cette classe collecte et maintient des statistiques détaillées sur l'utilisation
    du client WebSocket, incluant les messages, les octets transférés et les erreurs.
    
    Attributes:
        messages_received: Nombre de messages reçus.
        messages_sent: Nombre de messages envoyés.
        bytes_received: Nombre d'octets reçus.
        bytes_sent: Nombre d'octets envoyés.
        connection_start: Horodatage du début de connexion.
        reconnect_attempts: Nombre de tentatives de reconnexion.
        errors: Liste des erreurs rencontrées.
    """
    
    def __init__(self) -> None:
        self.messages_received = 0
        self.messages_sent = 0
        self.bytes_received = 0
        self.bytes_sent = 0
        self.connection_start = None
        self.reconnect_attempts = 0
        self.errors = []
        
    def record_message_received(self, message: str) -> None:
        """Enregistre la réception d'un message.
        
        Args:
            message: Le message reçu à enregistrer.
        """
        self.messages_received += 1
        self.bytes_received += len(message.encode(DEFAULT_ENCODING))
        
    def record_message_sent(self, message: str) -> None:
        """Enregistre l'envoi d'un message.
        
        Args:
            message: Le message envoyé à enregistrer.
        """
        self.messages_sent += 1
        self.bytes_sent += len(message.encode(DEFAULT_ENCODING))
        
    def record_error(self, error: Exception) -> None:
        """Enregistre une erreur rencontrée.
        
        Args:
            error: L'exception à enregistrer.
        """
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'type': type(error).__name__
        })
        
    def get_uptime(self) -> Optional[float]:
        """Calcule la durée de connexion active.
        
        Returns:
            Optional[float]: Durée en secondes depuis le début de la connexion,
                           ou None si pas de connexion active.
        """
        if self.connection_start:
            return (datetime.now() - self.connection_start).total_seconds()
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit les statistiques en dictionnaire.
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant toutes les statistiques.
        """
        return {
            'messages_received': self.messages_received,
            'messages_sent': self.messages_sent,
            'bytes_received': self.bytes_received,
            'bytes_sent': self.bytes_sent,
            'uptime_seconds': self.get_uptime(),
            'reconnect_attempts': self.reconnect_attempts,
            'error_count': len(self.errors),
            'recent_errors': self.errors[-ERROR_HISTORY_LIMIT:]  # Dernières erreurs
        }


class WebSocketClient:
    """Client WebSocket professionnel avec gestion d'état et reconnexion.
    
    Cette classe implémente un client WebSocket complet avec reconnexion automatique,
    gestion des états, ping/pong pour maintenir la connexion active, et système
    de gestionnaires de messages flexible.
    
    Args:
        uri: URI du serveur WebSocket.
        logger: Logger optionnel pour les messages de journalisation.
        reconnect: Active la reconnexion automatique si True.
        reconnect_interval: Intervalle entre les tentatives de reconnexion.
        max_reconnect_attempts: Nombre maximum de tentatives de reconnexion.
        ping_interval: Intervalle entre les pings.
        ping_timeout: Timeout pour la réponse au ping.
    """
    
    def __init__(
        self,
        uri: str,
        logger: Optional[logging.Logger] = None,
        reconnect: bool = True,
        reconnect_interval: float = RECONNECT_INTERVAL,
        max_reconnect_attempts: Optional[int] = None,
        ping_interval: float = PING_INTERVAL,
        ping_timeout: float = PING_TIMEOUT
    ) -> None:
        self.uri = uri
        self.logger = logger or logging.getLogger(__name__)
        self.reconnect = reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        
        self.state = ClientState.DISCONNECTED
        self.websocket = None
        self.statistics = ClientStatistics()
        self.handlers: Dict[str, List[Callable[..., Any]]] = {}  # Gestionnaires de messages par type
        self._tasks = []  # Tâches asynchrones actives
        self._running = False  # Indicateur d'exécution
        
    def on(self, message_type: str, handler: Callable[..., Any]) -> None:
        """Enregistre un gestionnaire de message pour un type spécifique.
        
        Args:
            message_type: Type de message à gérer (ou '*' pour tous).
            handler: Fonction callback à appeler pour ce type de message.
        """
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)
        
    def remove_handler(self, message_type: str, handler: Callable[..., Any]) -> None:
        """Supprime un gestionnaire spécifique.
        
        Args:
            message_type: Type de message du gestionnaire.
            handler: Fonction callback à supprimer.
        """
        if message_type in self.handlers:
            self.handlers[message_type].remove(handler)
            
    async def _set_state(self, state: ClientState) -> None:
        """Met à jour l'état du client et notifie les gestionnaires.
        
        Args:
            state: Nouvel état du client.
        """
        old_state = self.state
        self.state = state
        self.logger.info(f"State changed: {old_state.value} -> {state.value}")
        
        # Notifie les gestionnaires de changement d'état
        if 'state_change' in self.handlers:
            for handler in self.handlers['state_change']:
                await self._call_handler(handler, old_state, state)
                
    async def _call_handler(self, handler: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Appelle un gestionnaire de manière sécurisée.
        
        Gère automatiquement les fonctions synchrones et asynchrones,
        et capture les exceptions pour éviter l'interruption du client.
        
        Args:
            handler: Fonction callback à appeler.
            *args: Arguments positionnels pour le gestionnaire.
            **kwargs: Arguments nommés pour le gestionnaire.
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                handler(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Handler error: {e}", exc_info=True)
            
    async def _handle_message(self, message: str) -> None:
        """Traite un message entrant.
        
        Parse le message JSON et appelle les gestionnaires appropriés.
        
        Args:
            message: Message JSON reçu du serveur.
        """
        self.statistics.record_message_received(message)
        
        try:
            data = json.loads(message)
            message_type = data.get('type', 'unknown')
            
            # Appelle les gestionnaires enregistrés
            if message_type in self.handlers:
                for handler in self.handlers[message_type]:
                    await self._call_handler(handler, data)
                    
            # Appelle les gestionnaires génériques (wildcard)
            if '*' in self.handlers:
                for handler in self.handlers['*']:
                    await self._call_handler(handler, data)
                    
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON message: {e}")
            self.statistics.record_error(e)
            
    async def _ping_loop(self) -> None:
        """Envoie des pings périodiques pour maintenir la connexion active.
        
        Cette boucle s'exécute en arrière-plan pendant toute la durée
        de la connexion et ferme la connexion si le serveur ne répond pas.
        """
        while self._running and self.websocket:
            try:
                await asyncio.sleep(self.ping_interval)
                if self.websocket:
                    try:
                        pong_waiter = await self.websocket.ping()
                        await asyncio.wait_for(pong_waiter, timeout=self.ping_timeout)
                        self.logger.debug("Ping successful")
                    except (ConnectionClosed, WebSocketException):
                        self.logger.warning("Connection closed during ping")
                        break
            except asyncio.TimeoutError:
                self.logger.warning("Ping timeout")
                if self.websocket:
                    await self.websocket.close()
                break
            except asyncio.CancelledError:
                # La tâche est annulée, sortie propre
                break
            except Exception as e:
                self.logger.error(f"Ping error: {e}")
                break
                
    async def send(self, data: Dict[str, Any]) -> None:
        """Envoie un message au serveur.
        
        Args:
            data: Dictionnaire de données à sérialiser en JSON.
            
        Raises:
            ConnectionError: Si le WebSocket n'est pas connecté.
        """
        if not self.websocket:
            raise ConnectionError("WebSocket is not connected")
            
        try:
            message = json.dumps(data)
            await self.websocket.send(message)
            self.statistics.record_message_sent(message)
            self.logger.debug(f"Sent message: {data.get('type', 'unknown')}")
        except (ConnectionClosed, WebSocketException) as e:
            raise ConnectionError(f"WebSocket connection closed: {e}")
        
    async def connect(self) -> None:
        """Connecte au serveur WebSocket.
        
        Établit la connexion, démarre la boucle de ping et commence
        à écouter les messages entrants.
        
        Raises:
            ConnectionRefusedError: Si la connexion est refusée.
            Exception: Pour toute autre erreur de connexion.
        """
        await self._set_state(ClientState.CONNECTING)
        
        try:
            self.websocket = await websockets.connect(
                self.uri,
                ping_interval=None  # Nous gérons les pings nous-mêmes
            )
            await self._set_state(ClientState.CONNECTED)
            self.statistics.connection_start = datetime.now()
            self.logger.info(f"Connected to {self.uri}")
            
            # Démarre la tâche de ping
            ping_task = asyncio.create_task(self._ping_loop())
            self._tasks.append(ping_task)
            
            # Boucle de réception des messages
            try:
                async for message in self.websocket:
                    await self._handle_message(message)
            except ConnectionClosed as e:
                self.logger.info(f"Connection closed: {e}")
                raise
            except WebSocketException as e:
                self.logger.warning(f"WebSocket error: {e}")
                raise
                
        except ConnectionRefusedError:
            await self._set_state(ClientState.ERROR)
            self.logger.error(f"Connection refused to {self.uri}")
            raise
        except (ConnectionClosed, WebSocketException) as e:
            # Ces exceptions sont attendues lors de la fermeture
            self.logger.debug(f"WebSocket closed: {e}")
            raise
        except Exception as e:
            await self._set_state(ClientState.ERROR)
            self.logger.error(f"Connection error: {e}")
            self.statistics.record_error(e)
            raise
            
    async def disconnect(self) -> None:
        """Déconnecte du serveur.
        
        Arrête toutes les tâches asynchrones et ferme proprement
        la connexion WebSocket.
        """
        self._running = False
        
        # Annule toutes les tâches
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        # Vide la liste des tâches
        self._tasks.clear()
            
        # Ferme le WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                self.logger.debug(f"Error closing websocket: {e}")
            finally:
                self.websocket = None
            
        await self._set_state(ClientState.DISCONNECTED)
        self.logger.info("Disconnected")
        
    async def run(self) -> None:
        """Exécute le client avec reconnexion automatique.
        
        Boucle principale qui gère la connexion, la reconnexion automatique
        en cas d'erreur, et l'arrêt propre du client.
        """
        self._running = True
        reconnect_attempts = 0
        
        while self._running:
            try:
                await self.connect()
                reconnect_attempts = 0  # Réinitialise après une connexion réussie
                
            except asyncio.CancelledError:
                self.logger.info("Client cancelled")
                break
                
            except Exception as e:
                self.statistics.record_error(e)
                
                if not self.reconnect:
                    self.logger.error("Connection failed, reconnection disabled")
                    break
                    
                reconnect_attempts += 1
                self.statistics.reconnect_attempts = reconnect_attempts
                
                if self.max_reconnect_attempts and reconnect_attempts >= self.max_reconnect_attempts:
                    self.logger.error(f"Max reconnection attempts reached ({self.max_reconnect_attempts})")
                    break
                    
                await self._set_state(ClientState.RECONNECTING)
                self.logger.info(f"Reconnecting in {self.reconnect_interval}s (attempt {reconnect_attempts})")
                
                try:
                    await asyncio.sleep(self.reconnect_interval)
                except asyncio.CancelledError:
                    break
                    
        await self.disconnect()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Obtient les statistiques du client.
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant toutes les statistiques
                          du client, incluant l'état actuel et l'URI.
        """
        stats = self.statistics.to_dict()
        stats['current_state'] = self.state.value
        stats['uri'] = self.uri
        return stats