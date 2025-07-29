#!/usr/bin/env python3
"""Serveur WebSocket autonome pour le monitoring système.

Ce module fournit un serveur WebSocket indépendant qui collecte et diffuse
les données de monitoring système en temps réel à tous les clients connectés.

Classes:
    StandaloneWebSocketServer: Serveur WebSocket autonome pour le monitoring

Utilisation:
    python run_server.py [--host HOST] [--port PORT]
"""
import sys
import os
# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
import logging
from datetime import datetime
import websockets
import psutil
import platform
import subprocess
import socket
import argparse
from typing import Dict, Any, Set, List

# Solution : utiliser psutil directement pour les fréquences CPU
# et implémenter une version simplifiée des fonctions avancées localement

def get_cpu_max_frequency() -> float:
    """Récupère la fréquence maximale du CPU en MHz."""
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.max > 0:
            return cpu_freq.max
    except (AttributeError, RuntimeError, ValueError):
        pass
    
    # Si psutil échoue, essayer des méthodes spécifiques à l'OS
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["wmic", "cpu", "get", "MaxClockSpeed", "/value"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('MaxClockSpeed='):
                        return float(line.split('=')[1])
        except (subprocess.SubprocessError, ValueError, IndexError):
            pass
    
    return 0.0

def get_cpu_current_frequency() -> float:
    """Récupère la fréquence actuelle du CPU en MHz."""
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.current > 0:
            return cpu_freq.current
    except (AttributeError, RuntimeError, ValueError):
        pass
    
    # Si psutil échoue, essayer des méthodes spécifiques à l'OS
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["wmic", "cpu", "get", "CurrentClockSpeed", "/value"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('CurrentClockSpeed='):
                        return float(line.split('=')[1])
        except (subprocess.SubprocessError, ValueError, IndexError):
            pass
    
    return 0.0


from config import (
    WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_MAX_CLIENTS,
    WEBSOCKET_CLOSE_CODE_CAPACITY, WEBSOCKET_SEND_TIMEOUT,
    MONITORING_COLLECTION_INTERVAL, CPU_PERCENT_INTERVAL,
    DEFAULT_DISK_PATH,
    MEMORY_WARNING_THRESHOLD, MEMORY_CRITICAL_THRESHOLD,
    DISK_WARNING_THRESHOLD, DISK_CRITICAL_THRESHOLD
)

# Pour les GPU
try:
    import GPUtil
except ImportError:
    GPUtil = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StandaloneWebSocketServer:
    """Serveur WebSocket autonome pour diffuser les données de monitoring.
    
    Cette classe gère les connexions WebSocket, collecte les données système
    et les diffuse périodiquement à tous les clients connectés.
    
    Attributes:
        host: Adresse IP d'écoute du serveur
        port: Port d'écoute du serveur
        clients: Ensemble des clients WebSocket connectés
    """
    
    def __init__(self, host: str = WEBSOCKET_HOST, port: int = WEBSOCKET_PORT, max_clients: int = WEBSOCKET_MAX_CLIENTS) -> None:
        self.host: str = host
        self.port: int = port
        self.max_clients: int = max_clients
        self.clients: Set[Any] = set()
        self._running: bool = False
        
    async def register_client(self, websocket: Any) -> None:
        """Enregistre un nouveau client."""
        # Vérifier la limite de clients
        if len(self.clients) >= self.max_clients:
            logger.warning(f"Client limit reached ({self.max_clients}). Refusing connection from {websocket.remote_address}")
            await websocket.close(code=WEBSOCKET_CLOSE_CODE_CAPACITY, reason="Server at capacity")
            return
            
        self.clients.add(websocket)
        logger.info(f"New client connected: {websocket.remote_address}. Total: {len(self.clients)}")
        
        # Message de bienvenue
        await websocket.send(json.dumps({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to monitoring server"
        }))
        
    async def unregister_client(self, websocket: Any) -> None:
        """Désenregistre un client."""
        if websocket in self.clients:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")
            
    async def handle_client(self, websocket: Any) -> None:
        """Gère un client WebSocket."""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                    elif data.get("type") == "get_status":
                        await websocket.send(json.dumps({
                            "type": "status",
                            "connected_clients": len(self.clients),
                            "monitoring_active": self._running,
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

    @staticmethod
    def get_system_data() -> Dict[str, Any]:
        """Collecte les données système directement."""
        # Mémoire
        mem = psutil.virtual_memory()
        memory_data = {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percentage": mem.percent
        }
        
        # CPU - Utiliser directement les fonctions utilitaires si nécessaire
        cpu_percent = psutil.cpu_percent(interval=CPU_PERCENT_INTERVAL)
        cpu_freq = psutil.cpu_freq()
        
        # Déterminer les fréquences en utilisant les fonctions améliorées
        freq_max = cpu_freq.max if cpu_freq else 0
        freq_current = cpu_freq.current if cpu_freq else 0
        
        # Utiliser les fonctions améliorées si psutil retourne des valeurs incorrectes
        if freq_max == 2500 or freq_max == 0 or freq_max is None:
            better_freq = get_cpu_max_frequency()
            if better_freq > 0:
                freq_max = better_freq
        
        if freq_current == 0 or freq_current is None:
            better_current = get_cpu_current_frequency()
            if better_current > 0:
                freq_current = better_current
        
        cpu_data = {
            "usage_percent": cpu_percent,
            "core_count": psutil.cpu_count(logical=False),
            "logical_count": psutil.cpu_count(logical=True),
            "frequency_current": freq_current,
            "frequency_max": freq_max,
            "per_core_usage": psutil.cpu_percent(interval=CPU_PERCENT_INTERVAL, percpu=True)
        }
        
        # Disque
        disk = psutil.disk_usage('/')
        disk_data = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percentage": disk.percent,
            "path": DEFAULT_DISK_PATH
        }
        
        # OS
        os_data = {
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": socket.gethostname()
        }
        
        # GPU (si disponible)
        gpu_data = None
        
        # Essayer d'abord GPUtil
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_data = {
                        "name": gpu.name,
                        "driver_version": gpu.driver,
                        "memory_total": gpu.memoryTotal * 1024 * 1024,  # Convertir en bytes
                        "memory_used": gpu.memoryUsed * 1024 * 1024,
                        "memory_free": gpu.memoryFree * 1024 * 1024,
                        "memory_percentage": gpu.memoryUtil * 100,
                        "gpu_usage_percent": gpu.load * 100,
                        "temperature": gpu.temperature,
                        "power_draw": None,
                        "power_limit": None
                    }
            except (AttributeError, RuntimeError, ValueError):
                pass  # GPUtil non disponible ou erreur
        
        # Si GPUtil n'a pas fonctionné, essayer nvidia-smi directement
        if not gpu_data:
            try:
                # Obtenir les infos GPU via nvidia-smi
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=name,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu', 
                     '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Parser la sortie CSV
                    values = result.stdout.strip().split(', ')
                    if len(values) >= 7:
                        gpu_data = {
                            "name": values[0],
                            "driver_version": values[1],
                            "memory_total": int(values[2]) * 1024 * 1024,  # MB vers bytes
                            "memory_used": int(values[3]) * 1024 * 1024,
                            "memory_free": int(values[4]) * 1024 * 1024,
                            "memory_percentage": (int(values[3]) / int(values[2])) * 100,
                            "gpu_usage_percent": float(values[5]),
                            "temperature": float(values[6]) if values[6] != 'N/A' else None,
                            "power_draw": None,
                            "power_limit": None
                        }
            except (subprocess.SubprocessError, ValueError, FileNotFoundError, IndexError):
                pass  # nvidia-smi non disponible ou erreur
        
        return {
            "memory": memory_data,
            "processor": cpu_data,
            "disk": disk_data,
            "os": os_data,
            "gpu": gpu_data
        }
    
    @staticmethod
    def check_thresholds(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Vérifie les seuils et génère des alertes si nécessaire."""
        alerts = []
        timestamp = datetime.now().isoformat()
        
        # Vérifier les seuils de mémoire
        memory_percent = data["memory"]["percentage"]
        if memory_percent >= MEMORY_CRITICAL_THRESHOLD:
            alerts.append({
                "timestamp": timestamp,
                "component": "memory",
                "metric": "usage_percent",
                "value": memory_percent,
                "threshold": MEMORY_CRITICAL_THRESHOLD,
                "level": "CRITICAL",
                "message": f"Critical memory usage: {memory_percent:.1f}% (threshold: {MEMORY_CRITICAL_THRESHOLD}%)"
            })
        elif memory_percent >= MEMORY_WARNING_THRESHOLD:
            alerts.append({
                "timestamp": timestamp,
                "component": "memory",
                "metric": "usage_percent",
                "value": memory_percent,
                "threshold": MEMORY_WARNING_THRESHOLD,
                "level": "WARNING",
                "message": f"High memory usage: {memory_percent:.1f}% (threshold: {MEMORY_WARNING_THRESHOLD}%)"
            })
        
        # Vérifier les seuils de disque
        disk_percent = data["disk"]["percentage"]
        if disk_percent >= DISK_CRITICAL_THRESHOLD:
            alerts.append({
                "timestamp": timestamp,
                "component": "disk",
                "metric": "usage_percent",
                "value": disk_percent,
                "threshold": DISK_CRITICAL_THRESHOLD,
                "level": "CRITICAL",
                "message": f"Critical disk usage: {disk_percent:.1f}% (threshold: {DISK_CRITICAL_THRESHOLD}%)"
            })
        elif disk_percent >= DISK_WARNING_THRESHOLD:
            alerts.append({
                "timestamp": timestamp,
                "component": "disk",
                "metric": "usage_percent",
                "value": disk_percent,
                "threshold": DISK_WARNING_THRESHOLD,
                "level": "WARNING",
                "message": f"High disk usage: {disk_percent:.1f}% (threshold: {DISK_WARNING_THRESHOLD}%)"
            })
        
        return alerts
    
    async def collect_and_broadcast(self) -> None:
        """Collecte et diffuse les données de monitoring."""
        logger.info("Starting data collection")
        
        while self._running:
            try:
                # Collecter les données
                data = self.get_system_data()
                
                # Créer le message
                message: Dict[str, Any] = {
                    "type": "monitoring_data",
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "memory": data["memory"],
                        "processor": data["processor"],
                        "disk": data["disk"],
                        "system": data["os"]
                    }
                }
                
                # Ajouter GPU si disponible
                if data["gpu"]:
                    message["data"]["gpu"] = data["gpu"]
                
                # Vérifier les seuils et ajouter les alertes
                alerts = StandaloneWebSocketServer.check_thresholds(data)
                if alerts:
                    message["alerts"] = alerts
                
                # Envoyer à tous les clients de manière efficace
                if self.clients:
                    # Copier la liste pour éviter les modifications pendant l'itération
                    clients_copy = list(self.clients)
                    disconnected = set()
                    
                    # Sérialiser le message une seule fois
                    message_json = json.dumps(message)
                    
                    # Fonction pour envoyer à un client
                    async def send_to_client(client):
                        try:
                            await asyncio.wait_for(client.send(message_json), timeout=WEBSOCKET_SEND_TIMEOUT)
                        except (websockets.exceptions.WebSocketException, ConnectionError, asyncio.TimeoutError):
                            disconnected.add(client)
                        except Exception as exc:
                            logger.error(f"Error sending to {getattr(client, 'remote_address', 'unknown')}: {exc}")
                            disconnected.add(client)
                    
                    # Envoyer à tous les clients en parallèle
                    if clients_copy:
                        await asyncio.gather(
                            *[send_to_client(client) for client in clients_copy],
                            return_exceptions=True
                        )
                    
                    # Retirer les clients déconnectés
                    for client in disconnected:
                        await self.unregister_client(client)
                
            except (psutil.Error, ValueError, RuntimeError) as e:
                logger.error(f"Error during data collection: {e}")
                
            # Attendre avant la prochaine collecte
            await asyncio.sleep(MONITORING_COLLECTION_INTERVAL)
            
            
    async def start(self) -> None:
        """Démarre le serveur WebSocket."""
        self._running = True
        
        # Démarrer la collecte de données
        collect_task = asyncio.create_task(self.collect_and_broadcast())
        
        # Créer une fonction wrapper pour gérer la signature
        async def handle_wrapper(*args: Any) -> None:
            # Gérer différentes signatures de websockets
            if len(args) == 2:
                websocket, _ = args  # path non utilisé
            else:
                websocket = args[0]
            await self.handle_client(websocket)
        
        # Démarrer le serveur WebSocket
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        try:
            async with websockets.serve(handle_wrapper, self.host, self.port):
                # Attendre indéfiniment
                await asyncio.Future()
        except (KeyboardInterrupt, asyncio.CancelledError):
            # Arrêt propre
            logger.info("Stopping WebSocket server...")
            self._running = False
            
            # Annuler la tâche de collecte
            collect_task.cancel()
            try:
                await collect_task
            except asyncio.CancelledError:
                pass
            
            # Fermer toutes les connexions
            for client in list(self.clients):
                try:
                    await client.close()
                except (websockets.exceptions.WebSocketException, ConnectionError):
                    pass


def main() -> None:
    """Point d'entrée principal."""
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description='WebSocket monitoring server')
    parser.add_argument('--host', type=str, default=WEBSOCKET_HOST,
                        help=f'Host address to bind to (default: {WEBSOCKET_HOST})')
    parser.add_argument('--port', type=int, default=WEBSOCKET_PORT,
                        help=f'Port to bind to (default: {WEBSOCKET_PORT})')
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("Standalone WebSocket monitoring server")
    logger.info("=" * 50)

    server = StandaloneWebSocketServer(host=args.host, port=args.port)

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("\n\n Stopping WebSocket server...")

if __name__ == "__main__":
    main()