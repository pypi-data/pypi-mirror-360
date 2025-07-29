"""
Serveur WebSocket pour émettre les données de monitoring en temps réel.
Permet aux clients (y compris les containers Docker) de recevoir les données.
"""

import asyncio
import json
import logging
from typing import Set, Optional, Any, Dict
from datetime import datetime

import websockets
try:
    import psutil
except ImportError:
    psutil = None

from ..config import (
    WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_MAX_CLIENTS,
    WEBSOCKET_SEND_TIMEOUT,
    WEBSOCKET_BROADCAST_SEMAPHORE_LIMIT
)
from ..core.models import MonitoringSnapshot
from .realtime import RealtimeMonitoringService


class WebSocketMonitoringServer:
    """Serveur WebSocket pour diffuser les données de monitoring."""
    
    def __init__(self, host: str = WEBSOCKET_HOST, port: int = WEBSOCKET_PORT, max_clients: int = WEBSOCKET_MAX_CLIENTS) -> None:
        """Initialise le serveur WebSocket.

        Args:
            host (str): Adresse d'écoute (0.0.0.0 pour toutes les interfaces)
            port (int): Port d'écoute
            max_clients (int): Nombre maximum de clients connectés simultanément
        """
        self.host: str = host
        self.port: int = port
        self.max_clients: int = max_clients
        self.clients: Set[Any] = set()
        self.monitoring_service: Optional[RealtimeMonitoringService] = None
        self.server: Optional[Any] = None
        self._running: bool = False
        self._logger: logging.Logger = logging.getLogger(__name__)
        
        # Pool de workers pour le broadcast efficace
        self._broadcast_semaphore: asyncio.Semaphore = asyncio.Semaphore(WEBSOCKET_BROADCAST_SEMAPHORE_LIMIT)  # Limite de 50 envois concurrents
        
    @property
    def is_running(self) -> bool:
        """Indique si le serveur est en cours d'exécution."""
        return self._running
        
    async def register_client(self, websocket: Any) -> None:
        """Enregistre un nouveau client WebSocket.

        Args:
            websocket: Le client WebSocket
        """
        # Vérifier la limite de clients
        if len(self.clients) >= self.max_clients:
            self._logger.warning(f"Client limit reached ({self.max_clients}). Refusing connection from {websocket.remote_address}")
            await websocket.close(code=1008, reason="Server at capacity")
            return
            
        self.clients.add(websocket)
        self._logger.info(f"New client connected: {websocket.remote_address}. Total: {len(self.clients)}")
        
        # Envoyer un message de bienvenue
        await websocket.send(json.dumps({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to monitoring server"
        }))
        
    async def unregister_client(self, websocket: Any) -> None:
        """Désenregistre un client WebSocket.

        Args:
            websocket: Le client WebSocket
        """
        if websocket in self.clients:
            self.clients.remove(websocket)
            self._logger.info(f"Client disconnected: {websocket.remote_address}")
            
    async def broadcast_snapshot(self, snapshot: MonitoringSnapshot) -> None:
        """Diffuse un snapshot à tous les clients connectés.

        Args:
            snapshot: Le snapshot à diffuser
        """
        if not self.clients:
            return
            
        # Convertir le snapshot en dictionnaire
        data: Dict[str, Any] = {
            "type": "monitoring_data",
            "timestamp": snapshot.timestamp.isoformat(),
            "data": {
                "memory": {
                    "total": snapshot.memory_info.total,
                    "available": snapshot.memory_info.available,
                    "used": snapshot.memory_info.used,
                    "percentage": snapshot.memory_info.percentage
                },
                "processor": {
                    "usage_percent": snapshot.processor_info.usage_percent,
                    "core_count": snapshot.processor_info.core_count,
                    "logical_count": snapshot.processor_info.logical_count,
                    "frequency_current": snapshot.processor_info.frequency_current,
                    "frequency_max": snapshot.processor_info.frequency_max,
                    "per_core_usage": snapshot.processor_info.per_core_usage
                },
                "disk": {
                    "total": snapshot.disk_info.total,
                    "used": snapshot.disk_info.used,
                    "free": snapshot.disk_info.free,
                    "percentage": snapshot.disk_info.percentage,
                    "path": snapshot.disk_info.path
                },
                "system": {
                    "os_name": snapshot.os_info.name,
                    "os_version": snapshot.os_info.version,
                    "os_release": snapshot.os_info.release,
                    "architecture": snapshot.os_info.architecture,
                    "platform": snapshot.os_info.platform,
                    "machine": snapshot.os_info.machine,
                    "processor": snapshot.os_info.processor,
                    "python_version": snapshot.os_info.python_version,
                    "hostname": snapshot.os_info.hostname,
                    # Informations dynamiques (ajoutées si disponibles)
                    "processes": len(psutil.pids()) if psutil else None,
                    "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat() if psutil else None
                }
            }
        }
        
        # Ajouter les informations GPU si disponibles
        if hasattr(snapshot, 'gpu_info') and snapshot.gpu_info:
            data["data"]["gpu"] = {
                "name": snapshot.gpu_info.name,
                "driver_version": snapshot.gpu_info.driver_version,
                "memory_total": snapshot.gpu_info.memory_total,
                "memory_used": snapshot.gpu_info.memory_used,
                "memory_free": snapshot.gpu_info.memory_free,
                "memory_percentage": snapshot.gpu_info.memory_percentage,
                "gpu_usage_percent": snapshot.gpu_info.gpu_usage_percent,
                "temperature": snapshot.gpu_info.temperature,
                "power_draw": snapshot.gpu_info.power_draw,
                "power_limit": snapshot.gpu_info.power_limit
            }
        
        # Ajouter les alertes si disponibles
        if hasattr(snapshot, 'alerts') and snapshot.alerts:
            data["alerts"] = [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "component": alert.component,
                    "metric": alert.metric,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "level": alert.level.value,
                    "message": alert.message
                }
                for alert in snapshot.alerts
            ]
        
        message = json.dumps(data)
        
        # Envoyer à tous les clients de manière efficace
        if self.clients:
            # Utiliser une copie pour éviter les modifications pendant l'itération
            clients_copy = list(self.clients)
            disconnected_clients: Set[Any] = set()
            
            # Fonction pour envoyer à un client avec semaphore
            async def send_with_semaphore(client: Any) -> None:
                async with self._broadcast_semaphore:
                    try:
                        await asyncio.wait_for(client.send(message), timeout=WEBSOCKET_SEND_TIMEOUT)
                    except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError):
                        disconnected_clients.add(client)
                    except Exception as e:
                        self._logger.error(f"Error sending to client {getattr(client, 'remote_address', 'unknown')}: {e}")
                        disconnected_clients.add(client)
            
            # Envoyer à tous les clients en parallèle avec limitation par semaphore
            await asyncio.gather(
                *[send_with_semaphore(client) for client in clients_copy],
                return_exceptions=True
            )
            
            # Retirer les clients déconnectés
            for client in disconnected_clients:
                await self.unregister_client(client)
    
            
    async def handle_client(self, websocket: Any) -> None:
        """Gère la connexion d'un client WebSocket.

        Args:
            websocket: Le client WebSocket
        """
        # path parameter is kept for WebSocket protocol compatibility
        await self.register_client(websocket)
        
        try:
            # Garder la connexion ouverte
            async for message in websocket:
                # Traiter les messages du client si nécessaire
                try:
                    data = json.loads(message)
                    
                    # Gérer différents types de messages
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                    elif data.get("type") == "get_status":
                        await websocket.send(json.dumps({
                            "type": "status",
                            "connected_clients": len(self.clients),
                            "monitoring_active": self.monitoring_service is not None and self.monitoring_service.is_running,
                            "timestamp": datetime.now().isoformat()
                        }))
                        
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid message"
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
            
    async def monitoring_loop(self) -> None:
        """Boucle principale pour envoyer les données de monitoring."""
        # Cette méthode n'est plus utilisée car les données sont envoyées via l'exporteur
        pass
            
    async def start_server(self, monitoring_service: RealtimeMonitoringService) -> None:
        """Démarre le serveur WebSocket.

        Args:
            monitoring_service: Le service de monitoring à utiliser
        """
        self.monitoring_service = monitoring_service
        self._running = True
        
        # Créer une fonction wrapper pour gérer la signature
        async def handle_wrapper(*args: Any) -> None:
            # Gérer différentes signatures de websockets
            websocket = args[0]
            await self.handle_client(websocket)
        
        # Démarrer le serveur WebSocket
        self.server = await websockets.serve(
            handle_wrapper,
            self.host,
            self.port
        )
        
        self._logger.info(f"WebSocket server started on {self.host}:{self.port}")
        
        try:
            # Garder le serveur actif
            await asyncio.Future()
        finally:
            pass
            
    async def stop_server(self) -> None:
        """Arrête le serveur WebSocket."""
        self._running = False
        
        # Fermer toutes les connexions clients
        for client in list(self.clients):
            await client.close()
            
        # Fermer le serveur
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
        self._logger.info("WebSocket server stopped")
        
    def run(self, monitoring_service: RealtimeMonitoringService) -> None:
        """Lance le serveur WebSocket de manière synchrone.

        Args:
            monitoring_service: Le service de monitoring à utiliser
        """
        try:
            asyncio.run(self.start_server(monitoring_service))
        except KeyboardInterrupt:
            self._logger.info("Stopping WebSocket server...")