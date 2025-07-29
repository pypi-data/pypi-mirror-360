"""
Service principal de monitoring temps réel.
Coordination asynchrone de tous les composants de monitoring.
"""

import asyncio
import logging
from collections import deque
import time as time_module
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Deque, List

from ..config import (
    MONITOR_INTERVAL, EXPORT_INTERVAL, MAX_SNAPSHOTS_HISTORY,
    THREAD_POOL_WORKERS, DEFAULT_EXPORT_DIR,
    MAX_ERROR_COUNT,
    CLEANUP_INTERVAL, MAX_ALERTS_COUNT
)
from ..monitors.system import SystemMonitor
from ..alerts.manager import AlertManager
from ..exporters.json_exporter import JSONExporter
from ..core.models import MonitoringSnapshot
from ..core.enums import MonitoringStatus
from ..core.exceptions import ServiceStartupError, ServiceShutdownError, DataCollectionError


class RealtimeMonitoringService:
    """Service principal de monitoring temps réel.
    
    Gère la coordination asynchrone de tous les composants de monitoring.
    """

    def __init__(self,
                 monitor_interval: float = MONITOR_INTERVAL,
                 export_interval: float = EXPORT_INTERVAL,
                 max_snapshots_history: int = MAX_SNAPSHOTS_HISTORY,
                 export_dir: Optional[Path] = None,
                 max_workers: int = THREAD_POOL_WORKERS) -> None:
        """Initialise le service de monitoring.

        Args:
            monitor_interval: Intervalle de monitoring en secondes.
            export_interval: Intervalle d'export en secondes.
            max_snapshots_history: Taille maximale de l'historique.
            export_dir: Répertoire d'export personnalisé.
            max_workers: Nombre maximum de workers pour le thread pool.
        """
        self._monitor_interval: float = self._validate_interval(monitor_interval)
        self._export_interval: float = self._validate_interval(export_interval)

        # Composants principaux
        self._system_monitor: SystemMonitor = SystemMonitor()
        self._alert_manager: AlertManager = AlertManager()
        
        export_path = export_dir or Path(DEFAULT_EXPORT_DIR)
        self._exporter: JSONExporter = JSONExporter(export_path)

        # Thread pool executor pour les opérations CPU-bound
        # Utiliser thread_name_prefix pour faciliter le debugging
        self._executor: Optional[ThreadPoolExecutor] = None
        self._max_workers: int = max_workers

        # État du service
        self._status: MonitoringStatus = MonitoringStatus.STOPPED
        self._monitoring_task: Optional[asyncio.Task] = None
        self._export_task: Optional[asyncio.Task] = None
        self._current_snapshot: Optional[MonitoringSnapshot] = None
        self._snapshots_history: Deque[MonitoringSnapshot] = deque(maxlen=max_snapshots_history)
        self._history_ttl: float = 3600.0  # Garder l'historique pour 1 heure maximum
        self._last_history_cleanup: float = time_module.time()

        # Statistiques
        self._stats: Dict[str, Any] = {
            "start_time": None,
            "alerts_count": 0,
            "last_snapshot_time": None,
            "errors_count": 0,
            "last_export_time": None
        }

        # Configuration du logging
        self._setup_logging()

    @property
    def monitor_interval(self) -> float:
        """Retourne l'intervalle de monitoring.

        Returns:
            Intervalle de monitoring en secondes.
        """
        return self._monitor_interval

    @monitor_interval.setter
    def monitor_interval(self, value: float) -> None:
        """Définit l'intervalle de monitoring.

        Args:
            value: Nouvel intervalle en secondes.

        Raises:
            ValueError: Si l'intervalle est invalide.
        """
        self._monitor_interval = self._validate_interval(value)

    @property
    def export_interval(self) -> float:
        """Retourne l'intervalle d'export.

        Returns:
            Intervalle d'export en secondes.
        """
        return self._export_interval

    @export_interval.setter
    def export_interval(self, value: float) -> None:
        """Définit l'intervalle d'export.

        Args:
            value: Nouvel intervalle en secondes.

        Raises:
            ValueError: Si l'intervalle est invalide.
        """
        self._export_interval = self._validate_interval(value)

    @property
    def status(self) -> MonitoringStatus:
        """Retourne l'état du service.

        Returns:
            État actuel du service.
        """
        return self._status

    @property
    def is_running(self) -> bool:
        """Indique si le service fonctionne.

        Returns:
            True si le service est en cours d'exécution, False sinon.
        """
        return self._status == MonitoringStatus.RUNNING

    @property
    def current_snapshot(self) -> Optional[MonitoringSnapshot]:
        """Retourne l'instantané actuel.

        Returns:
            Instantané actuel du monitoring ou None si aucun disponible.
        """
        return self._current_snapshot

    @property
    def statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du service.

        Returns:
            Dictionnaire contenant les statistiques du service.
        """
        stats = self._stats.copy()
        stats.update({
            "status": self._status.value,
            "snapshots_in_history": len(self._snapshots_history),
            "system_monitor_healthy": self._system_monitor.is_healthy(),
            "alert_manager_stats": self._alert_manager.get_statistics()
        })
        return stats

    @property
    def alert_manager(self) -> AlertManager:
        """Retourne le gestionnaire d'alertes.

        Returns:
            Instance du gestionnaire d'alertes.
        """
        return self._alert_manager

    @property
    def system_monitor(self) -> SystemMonitor:
        """Retourne le moniteur système.

        Returns:
            Instance du moniteur système.
        """
        return self._system_monitor

    @property
    def exporter(self) -> JSONExporter:
        """Retourne l'exporteur de données.

        Returns:
            Instance de l'exporteur JSON.
        """
        return self._exporter

    @staticmethod
    def _validate_interval(interval: float) -> float:
        """Valide un intervalle de temps.

        Args:
            interval: Intervalle à valider en secondes.

        Returns:
            Intervalle validé.

        Raises:
            ValueError: Si l'intervalle est invalide.
        """
        if interval <= 0:
            raise ValueError("Interval must be positive")
        if interval > 3600:  # Max 1 heure
            raise ValueError("Interval must not exceed 1 hour")
        return interval

    def _setup_logging(self) -> None:
        """Configure le système de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self._logger = logging.getLogger(f"{__name__}.RealtimeMonitoringService")

    async def start(self) -> None:
        """Démarre le service de monitoring.

        Raises:
            ServiceStartupError: En cas d'erreur de démarrage.
        """
        if self._status == MonitoringStatus.RUNNING:
            self._logger.warning("Service is already running")
            return

        if self._status == MonitoringStatus.STARTING:
            self._logger.warning("Service is already starting")
            return

        try:
            self._status = MonitoringStatus.STARTING
            self._logger.info("Starting real-time monitoring service")

            # Initialisation des composants
            self._system_monitor.initialize()
            
            # Créer le ThreadPoolExecutor uniquement quand nécessaire
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix="monitoring-"
                )
            
            # Réinitialisation des statistiques avec un timestamp unique
            service_start_time = datetime.now()
            self._stats["start_time"] = service_start_time
            self._stats["alerts_count"] = 0
            self._stats["errors_count"] = 0

            # Passage en mode RUNNING avant de démarrer les tâches
            self._status = MonitoringStatus.RUNNING
            
            # Démarrage des tâches en arrière-plan
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            # Export désactivé - suppression de la tâche d'export automatique
            # self._export_task = asyncio.create_task(self._export_loop())

            # Attente d'une première collecte
            await asyncio.sleep(max(0.1, self._monitor_interval))
            
            self._logger.info("Monitoring service started successfully")

        except Exception as e:
            self._status = MonitoringStatus.ERROR
            self._logger.error(f"Error during startup: {e}")
            await self._cleanup_tasks()
            raise ServiceStartupError(f"Unable to start service: {e}")

    async def stop(self) -> None:
        """Arrête le service de monitoring.

        Raises:
            ServiceShutdownError: En cas d'erreur d'arrêt.
        """
        if self._status == MonitoringStatus.STOPPED:
            return

        if self._status == MonitoringStatus.STOPPING:
            self._logger.warning("Service is already stopping")
            return

        try:
            self._status = MonitoringStatus.STOPPING
            self._logger.info("Stopping monitoring service...")

            # Arrêt des tâches
            await self._cleanup_tasks()

            self._status = MonitoringStatus.STOPPED
            self._logger.info("Service stopped successfully")

        except Exception as e:
            self._status = MonitoringStatus.ERROR
            self._logger.error(f"Error during shutdown: {e}")
            raise ServiceShutdownError(f"Error stopping service: {e}")

    async def _cleanup_tasks(self) -> None:
        """Nettoie les tâches asynchrones."""
        tasks_to_cancel = []
        
        if self._monitoring_task and not self._monitoring_task.done():
            tasks_to_cancel.append(self._monitoring_task)
        
        if self._export_task and not self._export_task.done():
            tasks_to_cancel.append(self._export_task)

        # Annulation des tâches
        for task in tasks_to_cancel:
            task.cancel()

        # Attente de l'arrêt complet
        if tasks_to_cancel:
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

        # Fermer le thread pool executor de manière plus sûre
        try:
            # Annuler toutes les futures en attente
            self._executor.shutdown(wait=False, cancel_futures=True)
        except Exception as e:
            self._logger.error(f"Error closing executor: {e}")
        finally:
            self._executor = None

        self._monitoring_task = None
        self._export_task = None

    async def _monitoring_loop(self) -> None:
        """Boucle principale de monitoring."""
        while self._status in (MonitoringStatus.STARTING, MonitoringStatus.RUNNING):
            try:
                await self._collect_system_data()
                await asyncio.sleep(self._monitor_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in monitoring loop: {e}")
                # Limite errors_count pour éviter overflow après très longue exécution
                if self._stats["errors_count"] < MAX_ERROR_COUNT:  # Prevent overflow
                    self._stats["errors_count"] += 1
                await asyncio.sleep(1)  # Pause avant retry



    async def _collect_system_data(self) -> None:
        """Collecte les données système de manière asynchrone.

        Raises:
            DataCollectionError: En cas d'erreur de collecte.
        """
        try:
            # Capturer le timestamp une seule fois pour tout le cycle de collecte
            collection_timestamp = datetime.now()
            
            # Collecte des données en parallèle en réutilisant le ThreadPoolExecutor
            loop = asyncio.get_event_loop()
            
            # Vérifier que l'executor existe
            if self._executor is None:
                raise DataCollectionError("ThreadPoolExecutor not initialized")
            
            # Exécuter en parallèle avec des tuples vides explicites pour les args
            # noinspection PyTypeChecker
            memory_info, processor_info, disk_info, os_info = await asyncio.gather(
                loop.run_in_executor(self._executor, self._system_monitor.memory_monitor.get_data, *()),
                loop.run_in_executor(self._executor, self._system_monitor.processor_monitor.get_data, *()),
                loop.run_in_executor(self._executor, self._system_monitor.disk_monitor.get_data, *()),
                loop.run_in_executor(self._executor, self._system_monitor.os_monitor.get_data, *())
            )

            # Création de l'instantané avec le timestamp unique
            snapshot = MonitoringSnapshot(
                timestamp=collection_timestamp,
                memory_info=memory_info,
                processor_info=processor_info,
                disk_info=disk_info,
                os_info=os_info,
                alerts=[]
            )

            # Vérification des alertes (cette opération est rapide et peut rester synchrone)
            alerts = self._alert_manager.check_thresholds(snapshot)
            snapshot.alerts = alerts

            # Mise à jour de l'état
            self._current_snapshot = snapshot
            self._snapshots_history.append(snapshot)
            
            # Nettoyer l'historique périodiquement (toutes les 60 secondes)
            current_time = time_module.time()
            if current_time - self._last_history_cleanup > CLEANUP_INTERVAL:
                self._cleanup_old_snapshots()
                self._last_history_cleanup = current_time

            # Mise à jour des statistiques avec le même timestamp
            # Limite alerts_count pour éviter overflow après très longue exécution
            if self._stats["alerts_count"] < MAX_ALERTS_COUNT:  # Prevent overflow
                self._stats["alerts_count"] += len(alerts)
            self._stats["last_snapshot_time"] = collection_timestamp

            # Log des alertes critiques
            for alert in alerts:
                if alert.level.value == "critical":
                    self._logger.error(alert.message)
                else:
                    self._logger.warning(alert.message)

        except Exception as e:
            self._logger.error(f"Error during data collection: {e}")
            # Limite errors_count pour éviter overflow après très longue exécution
            if self._stats["errors_count"] < 1000000:  # 1 million max
                self._stats["errors_count"] += 1
            raise DataCollectionError(f"Collection error: {e}")

    def get_system_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'état actuel du système.

        Returns:
            Dictionnaire contenant le résumé du système.
        """
        if not self._current_snapshot:
            return {
                "status": "no_data",
                "service_status": self._status.value,
                "timestamp": self._stats.get("last_snapshot_time", datetime.now()).isoformat()
            }

        snapshot = self._current_snapshot

        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "status": "alert" if snapshot.alerts else "normal",
            "service_status": self._status.value,
            "memory": {
                "usage_percent": round(snapshot.memory_info.percentage, 1),
                "used_gb": round(snapshot.memory_info.used / (1024**3), 2),
                "total_gb": round(snapshot.memory_info.total / (1024**3), 2),
                "available_gb": round(snapshot.memory_info.available / (1024**3), 2)
            },
            "cpu": {
                "usage_percent": round(snapshot.processor_info.usage_percent, 1),
                "core_count": snapshot.processor_info.core_count,
                "logical_count": snapshot.processor_info.logical_count,
                "frequency_mhz": round(snapshot.processor_info.frequency_current, 1)
            },
            "disk": {
                "usage_percent": round(snapshot.disk_info.percentage, 1),
                "free_gb": round(snapshot.disk_info.free / (1024**3), 2),
                "total_gb": round(snapshot.disk_info.total / (1024**3), 2),
                "used_gb": round(snapshot.disk_info.used / (1024**3), 2),
                "path": snapshot.disk_info.path
            },
            "alerts": len(snapshot.alerts),
            "service_stats": self.statistics
        }

    def get_snapshots_history(self, count: Optional[int] = None) -> List[MonitoringSnapshot]:
        """Retourne l'historique des snapshots.

        Args:
            count: Nombre de snapshots à retourner. Si None, retourne tout l'historique.

        Returns:
            Liste des snapshots de monitoring.
        """
        if count is None:
            return list(self._snapshots_history)
        
        return list(self._snapshots_history)[-count:] if count > 0 else []

    async def force_export(self) -> None:
        """Force un export immédiat des données actuelles.

        Raises:
            ExportError: En cas d'erreur d'export.
        """
        if self._current_snapshot:
            await self._exporter.export_snapshot(self._current_snapshot)
            self._stats["last_export_time"] = self._current_snapshot.timestamp
            self._logger.info("Forced export completed")

    def configure_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Configure les seuils d'alerte.

        Args:
            thresholds: Dictionnaire des seuils au format {composant_niveau: valeur}.
        """
        for key, value in thresholds.items():
            if "_" in key:
                component, level = key.split("_", 1)
                self._alert_manager.set_threshold(component, level, value)

    def get_health_report(self) -> Dict[str, Any]:
        """Génère un rapport de santé complet du service.

        Returns:
            Dictionnaire contenant le rapport de santé détaillé.
        """
        return {
            "service": {
                "status": self._status.value,
                "healthy": self._status == MonitoringStatus.RUNNING,
                "uptime_seconds": (datetime.now() - self._stats["start_time"]).total_seconds() if self._stats.get("start_time") else 0
            },
            "components": self._system_monitor.get_health_status(),
            "statistics": self.statistics,
            "configuration": {
                "monitor_interval": self._monitor_interval,
                "export_interval": self._export_interval,
                "max_snapshots_history": self._snapshots_history.maxlen
            }
        }
    
    def _cleanup_old_snapshots(self) -> None:
        """Nettoie les snapshots trop anciens de l'historique.
        
        Garde seulement les snapshots de moins d'une heure.
        Utilise un nettoyage in-place pour éviter la double allocation mémoire.
        """
        try:
            current_time = time_module.time()
            cutoff_time = current_time - self._history_ttl
            
            # Compter le nombre d'éléments à supprimer depuis le début
            items_to_remove = 0
            for snapshot in self._snapshots_history:
                snapshot_time = snapshot.timestamp.timestamp()
                if snapshot_time <= cutoff_time:
                    items_to_remove += 1
                else:
                    break  # Les snapshots sont ordonnés par temps
            
            # Supprimer les éléments obsolètes depuis le début
            for _ in range(items_to_remove):
                try:
                    self._snapshots_history.popleft()
                except IndexError:
                    break  # La deque est vide
                    
        except Exception as e:
            self._logger.error(f"Error cleaning history: {e}")

