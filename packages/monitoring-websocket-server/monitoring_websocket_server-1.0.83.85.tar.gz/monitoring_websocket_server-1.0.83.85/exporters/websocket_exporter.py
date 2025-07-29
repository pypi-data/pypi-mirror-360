"""
Exporteur WebSocket pour diffuser les données de monitoring en temps réel.
Intégration avec le système d'export existant.
"""

import asyncio
import logging
import threading
from typing import List, Optional, Dict, Any

import websockets

from ..config import WEBSOCKET_HOST, WEBSOCKET_PORT
from ..core.models import MonitoringSnapshot
from ..services.websocket_server import WebSocketMonitoringServer


class WebSocketExporter:
    """Exporteur qui diffuse les données via WebSocket."""
    
    def __init__(self, host: str = WEBSOCKET_HOST, port: int = WEBSOCKET_PORT) -> None:
        """Initialise l'exporteur WebSocket.

        Args:
            host (str): Adresse d'écoute
            port (int): Port d'écoute
        """
        self.host: str = host
        self.port: int = port
        self.websocket_server: WebSocketMonitoringServer = WebSocketMonitoringServer(host, port)
        self._server_thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._initialized: bool = False
        
    def initialize(self) -> None:
        """Initialise l'exporteur WebSocket."""
        self._logger.info(f"Initializing WebSocket exporter on {self.host}:{self.port}")
        self._initialized = True
        
    async def export_snapshot(self, snapshot: MonitoringSnapshot) -> None:
        """Exporte un snapshot via WebSocket.

        Args:
            snapshot: Le snapshot à exporter
        """
        if not self._initialized or not self.websocket_server.is_running:
            return
            
        await self.websocket_server.broadcast_snapshot(snapshot)
    
    def _do_export(self, snapshots: List[MonitoringSnapshot]) -> None:
        """Exporte les snapshots via WebSocket.

        Args:
            snapshots: Liste des snapshots à exporter
        """
        if not snapshots:
            return
            
        # Prendre le dernier snapshot
        latest_snapshot = snapshots[-1]
        
        # Si le serveur n'est pas encore démarré, on ignore
        if not self._loop or not self.websocket_server.is_running:
            return
            
        # Envoyer le snapshot de manière asynchrone
        future = asyncio.run_coroutine_threadsafe(
            self.websocket_server.broadcast_snapshot(latest_snapshot),
            self._loop
        )
        
        try:
            # Attendre que l'envoi soit terminé (avec timeout)
            future.result(timeout=1.0)
        except Exception as e:
            self._logger.error(f"Error during WebSocket broadcast: {e}")
            
    def start_server(self) -> None:
        """Démarre le serveur WebSocket dans un thread séparé."""
        if self._server_thread and self._server_thread.is_alive():
            self._logger.warning("WebSocket server is already running")
            return
            
        def run_server() -> None:
            # Créer un nouvel event loop pour ce thread
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            try:
                # Démarrer le serveur sans monitoring_service (on utilisera broadcast_snapshot)
                self._loop.run_until_complete(self._start_server_async())
            except Exception as e:
                self._logger.error(f"Error in WebSocket server: {e}")
            finally:
                if self._loop:
                    self._loop.close()
                    self._loop = None
                
        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()
        
        # Attendre que le serveur soit prêt
        import time
        time.sleep(1)
        
    async def _start_server_async(self) -> None:
        """Démarre le serveur WebSocket de manière asynchrone."""
        self.websocket_server._running = True
        
        # Créer une fonction wrapper pour gérer la signature
        async def handle_wrapper(*args: Any) -> None:
            # Gérer différentes signatures de websockets
            websocket = args[0]
            await self.websocket_server.handle_client(websocket)
        
        # Démarrer le serveur
        self.websocket_server.server = await websockets.serve(
            handle_wrapper,
            self.websocket_server.host,
            self.websocket_server.port
        )
        
        self._logger.info(f"WebSocket server started on {self.host}:{self.port}")
        
        # Garder le serveur actif
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
            
    def stop_server(self) -> None:
        """Arrête le serveur WebSocket."""
        if self._loop and self.websocket_server.is_running:
            # Arrêter le serveur de manière asynchrone
            future = asyncio.run_coroutine_threadsafe(
                self.websocket_server.stop_server(),
                self._loop
            )
            
            try:
                future.result(timeout=5.0)
            except Exception as e:
                self._logger.error(f"Error stopping server: {e}")
                
            # Arrêter la boucle d'événements
            def stop_loop():
                self._loop.stop()
            # noinspection PyTypeChecker
            self._loop.call_soon_threadsafe(stop_loop)
            
        if self._server_thread:
            self._server_thread.join(timeout=5.0)
            
    def get_export_info(self) -> Dict[str, Any]:
        """Retourne les informations sur l'export WebSocket.

        Returns:
            Dict[str, Any]: Informations de configuration
        """
        return {
            "type": "websocket",
            "host": self.host,
            "port": self.port,
            "server_running": self.websocket_server.is_running,
            "connected_clients": len(self.websocket_server.clients)
        }
        
    def __del__(self) -> None:
        """Destructeur pour s'assurer que le serveur est arrêté."""
        try:
            self.stop_server()
        except (RuntimeError, AttributeError, TypeError, OSError):
            pass  # Ignorer les erreurs dans le destructeur