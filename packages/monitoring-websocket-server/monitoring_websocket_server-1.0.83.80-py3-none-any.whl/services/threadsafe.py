"""Service de monitoring thread-safe avec isolation complète.

Wrapper qui isole le contexte asynchrone dans un thread séparé.
"""

import asyncio
import logging
import queue
import threading
from collections import deque
from typing import Any, Optional, Dict, List, Callable, Deque

from ..config import (
    EXPORT_INTERVAL, DATA_QUEUE_SIZE,
    COMMAND_QUEUE_SIZE, RESPONSE_QUEUE_SIZE, LAST_ALERTS_DEQUE_SIZE,
    SERVICE_START_TIMEOUT, SERVICE_STOP_TIMEOUT,
    EXPORT_RESPONSE_TIMEOUT, MAIN_LOOP_DELAY,
    CPU_USAGE_CHANGE_THRESHOLD, MEMORY_USAGE_CHANGE_THRESHOLD,
    DISK_USAGE_CHANGE_THRESHOLD
)
from .realtime import RealtimeMonitoringService
from ..core.models import Alert
from ..core.exceptions import ServiceStartupError, ServiceShutdownError


class ThreadSafeMonitoringService:
    """Wrapper thread-safe qui isole complètement le contexte asynchrone du service.
    
    Permet d'utiliser le service de monitoring dans n'importe quelle application
    sans conflit avec d'autres contextes asynchrones.
    """

    def __init__(self,
                 monitor_interval: float = 0.5,
                 export_interval: float = EXPORT_INTERVAL,
                 data_queue_size: int = DATA_QUEUE_SIZE,
                 export_dir: Optional[str] = None) -> None:
        """Initialise le service de monitoring thread-safe.

        Args:
            monitor_interval: Intervalle de monitoring en secondes.
            export_interval: Intervalle d'export en secondes.
            data_queue_size: Taille de la queue de données.
            export_dir: Répertoire d'export personnalisé.
        """
        self._monitor_interval: float = monitor_interval
        self._export_interval: float = export_interval
        self._export_dir: Optional[str] = export_dir

        # Communication inter-thread
        self._data_queue: queue.Queue = queue.Queue(maxsize=data_queue_size)
        self._command_queue: queue.Queue = queue.Queue(maxsize=COMMAND_QUEUE_SIZE)  # Limite des commandes
        self._response_queue: queue.Queue = queue.Queue(maxsize=RESPONSE_QUEUE_SIZE)  # Limite des réponses

        # État du service
        self._thread: Optional[threading.Thread] = None
        self._stop_event: threading.Event = threading.Event()
        self._ready_event: threading.Event = threading.Event()
        self._is_running: bool = False

        # Cache des dernières données
        self._last_summary: Optional[Dict[str, Any]] = None
        self._last_alerts: Deque[Alert] = deque(maxlen=LAST_ALERTS_DEQUE_SIZE)  # Limite des dernières alertes
        self._lock: threading.Lock = threading.Lock()

        # Callbacks
        self._alert_callbacks: List[Callable[[Alert], None]] = []
        self._data_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # Configuration du logging
        self._logger = logging.getLogger(f"{__name__}.ThreadSafe")

    @property
    def is_running(self) -> bool:
        """Retourne l'état du service.

        Returns:
            True si le service est en cours d'exécution, False sinon.
        """
        return self._is_running

    @property
    def monitor_interval(self) -> float:
        """Retourne l'intervalle de monitoring.

        Returns:
            Intervalle de monitoring en secondes.
        """
        return self._monitor_interval

    @property
    def export_interval(self) -> float:
        """Retourne l'intervalle d'export.

        Returns:
            Intervalle d'export en secondes.
        """
        return self._export_interval

    def start(self, timeout: float = SERVICE_START_TIMEOUT) -> bool:
        """Démarre le service de monitoring dans un thread séparé.

        Args:
            timeout: Timeout pour le démarrage en secondes.

        Returns:
            True si le démarrage a réussi.

        Raises:
            ServiceStartupError: En cas d'erreur de démarrage.
        """
        if self._is_running:
            self._logger.warning("Service is already running")
            return True

        try:
            # Réinitialisation des événements
            self._stop_event.clear()
            self._ready_event.clear()

            # Création et démarrage du thread
            self._thread = threading.Thread(
                target=self._run_async_service,
                name="MonitoringService",
                daemon=True
            )
            self._thread.start()

            # Attente du démarrage
            if self._ready_event.wait(timeout):
                self._is_running = True
                self._logger.info("Monitoring service started successfully")
                return True
            else:
                self._logger.error(f"Timeout during service startup ({timeout}s)")
                self.stop()
                raise ServiceStartupError(f"Startup timeout ({timeout}s)")

        except Exception as e:
            self._logger.error(f"Error during startup: {e}")
            raise ServiceStartupError(f"Unable to start service: {e}")

    def stop(self, timeout: float = SERVICE_STOP_TIMEOUT) -> bool:
        """Arrête le service de monitoring.

        Args:
            timeout: Timeout pour l'arrêt en secondes.

        Returns:
            True si l'arrêt a réussi.

        Raises:
            ServiceShutdownError: En cas d'erreur d'arrêt.
        """
        if not self._is_running:
            return True

        try:
            self._logger.info("Stopping monitoring service...")

            # Signal d'arrêt
            self._stop_event.set()

            # Attente de l'arrêt du thread
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout)

                if self._thread.is_alive():
                    self._logger.warning("Thread did not stop in time")
                    raise ServiceShutdownError(f"Shutdown timeout ({timeout}s)")

            self._is_running = False
            self._thread = None
            self._logger.info("Service stopped successfully")
            return True

        except Exception as e:
            self._logger.error(f"Error during shutdown: {e}")
            raise ServiceShutdownError(f"Shutdown error: {e}")

    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les données actuelles du système.

        Returns:
            Dictionnaire des données actuelles ou None si aucune donnée disponible.
        """
        with self._lock:
            return self._last_summary.copy() if self._last_summary else None

    def get_recent_alerts(self, count: int = 10) -> List[Alert]:
        """Récupère les alertes récentes.

        Args:
            count: Nombre d'alertes à retourner.

        Returns:
            Liste des alertes récentes.
        """
        with self._lock:
            return self._last_alerts[-count:] if self._last_alerts else []

    def set_alert_threshold(self, component: str, level: str, value: float) -> bool:
        """Définit un seuil d'alerte.

        Args:
            component: Composant (memory, cpu, disk).
            level: Niveau (warning, critical).
            value: Valeur du seuil.

        Returns:
            True si la configuration a réussi.
        """
        try:
            command = {
                "action": "set_threshold",
                "component": component,
                "level": level,
                "value": value
            }
            self._command_queue.put(command, timeout=1.0)

            # Attente de la réponse
            response = self._response_queue.get(timeout=2.0)
            return response.get("success", False)

        except queue.Empty:
            self._logger.error("Timeout during threshold configuration")
            return False
        except Exception as e:
            self._logger.error(f"Error during configuration: {e}")
            return False

    def configure_export(self, compress: bool = False, pretty_print: bool = True) -> bool:
        """Configure les options d'export.

        Args:
            compress: Activer la compression.
            pretty_print: Formater le JSON.

        Returns:
            True si la configuration a réussi.
        """
        try:
            command = {
                "action": "configure_export",
                "compress": compress,
                "pretty_print": pretty_print
            }
            self._command_queue.put(command, timeout=1.0)

            response = self._response_queue.get(timeout=2.0)
            return response.get("success", False)

        except queue.Empty:
            self._logger.error("Timeout during export configuration")
            return False
        except Exception as e:
            self._logger.error(f"Error during export configuration: {e}")
            return False

    def force_export(self) -> bool:
        """Force un export immédiat.

        Returns:
            True si l'export a réussi.
        """
        try:
            command = {"action": "force_export"}
            self._command_queue.put(command, timeout=1.0)

            response = self._response_queue.get(timeout=EXPORT_RESPONSE_TIMEOUT)
            return response.get("success", False)

        except queue.Empty:
            self._logger.error("Timeout during forced export")
            return False
        except Exception as e:
            self._logger.error(f"Error during forced export: {e}")
            return False

    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Ajoute un callback pour les nouvelles alertes.

        Args:
            callback: Fonction à appeler lors d'une nouvelle alerte.
        """
        with self._lock:
            if callback not in self._alert_callbacks:
                self._alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Supprime un callback d'alerte.

        Args:
            callback: Fonction à supprimer de la liste des callbacks.
        """
        with self._lock:
            if callback in self._alert_callbacks:
                self._alert_callbacks.remove(callback)

    def add_data_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Ajoute un callback pour les nouvelles données.

        Args:
            callback: Fonction à appeler lors de nouvelles données.
        """
        with self._lock:
            if callback not in self._data_callbacks:
                self._data_callbacks.append(callback)

    def remove_data_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Supprime un callback de données.

        Args:
            callback: Fonction à supprimer de la liste des callbacks.
        """
        with self._lock:
            if callback in self._data_callbacks:
                self._data_callbacks.remove(callback)

    def get_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques du service.

        Returns:
            Dictionnaire contenant les statistiques du service.
        """
        current_data = self.get_current_data()
        if current_data and "service_stats" in current_data:
            stats = current_data["service_stats"].copy()
            stats.update({
                "thread_alive": self._thread.is_alive() if self._thread else False,
                "alert_callbacks_count": len(self._alert_callbacks),
                "data_callbacks_count": len(self._data_callbacks)
            })
            return stats
        return {"thread_alive": False}

    def get_health_status(self) -> Dict[str, Any]:
        """Retourne le statut de santé du service.

        Returns:
            Dictionnaire contenant le statut de santé détaillé.
        """
        return {
            "service_running": self._is_running,
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "data_available": self._last_summary is not None,
            "alert_count": len(self._last_alerts),
            "queue_size": self._data_queue.qsize(),
            "command_queue_size": self._command_queue.qsize()
        }

    def _run_async_service(self) -> None:
        """Point d'entrée du thread asynchrone.
        
        Crée sa propre boucle d'événements isolée.
        """
        try:
            # Création d'une nouvelle boucle d'événements pour ce thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Exécution du service asynchrone
            loop.run_until_complete(self._async_main())

        except Exception as e:
            self._logger.error(f"Error in async thread: {e}")
        finally:
            # Nettoyage
            try:
                loop = asyncio.get_event_loop()
                loop.close()
            except (RuntimeError, AttributeError):
                pass

    async def _async_main(self) -> None:
        """Fonction principale asynchrone du service."""
        service = None
        try:
            # Création du service
            from pathlib import Path
            
            kwargs: Dict[str, Any] = {
                "monitor_interval": self._monitor_interval,
                "export_interval": self._export_interval
            }
            
            if self._export_dir:
                kwargs["export_dir"] = Path(self._export_dir)
            
            service = RealtimeMonitoringService(**kwargs)

            # Démarrage du service
            await service.start()

            # Signal que le service est prêt
            self._ready_event.set()

            # Boucle principale simplifiée
            while not self._stop_event.is_set():
                try:
                    # Traitement des commandes
                    await self._process_commands(service)

                    # Mise à jour des données
                    await self._update_data_cache(service)

                    # Pause courte
                    await asyncio.sleep(MAIN_LOOP_DELAY)

                except Exception as e:
                    self._logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(0.5)

        except Exception as e:
            self._logger.error(f"Error during service initialization: {e}")
        finally:
            # Arrêt propre du service
            if service:
                try:
                    await service.stop()
                except Exception as e:
                    self._logger.error(f"Error during service shutdown: {e}")

    async def _process_commands(self, service: RealtimeMonitoringService) -> None:
        """Traite les commandes de configuration.

        Args:
            service: Instance du service de monitoring temps réel.
        """
        try:
            while True:
                command = self._command_queue.get_nowait()

                if command["action"] == "set_threshold":
                    try:
                        service.alert_manager.set_threshold(
                            command["component"],
                            command["level"],
                            command["value"]
                        )
                        self._response_queue.put({"success": True})
                    except Exception as e:
                        self._logger.error(f"Error during configuration: {e}")
                        self._response_queue.put({"success": False, "error": str(e)})

                elif command["action"] == "configure_export":
                    try:
                        service.exporter.compress = command["compress"]
                        service.exporter.pretty_print = command["pretty_print"]
                        self._response_queue.put({"success": True})
                    except Exception as e:
                        self._logger.error(f"Export configuration error: {e}")
                        self._response_queue.put({"success": False, "error": str(e)})

                elif command["action"] == "force_export":
                    try:
                        await service.force_export()
                        self._response_queue.put({"success": True})
                    except Exception as e:
                        self._logger.error(f"Forced export error: {e}")
                        self._response_queue.put({"success": False, "error": str(e)})

        except queue.Empty:
            pass  # Pas de commandes en attente

    async def _update_data_cache(self, service: RealtimeMonitoringService) -> None:
        """Met à jour le cache des données.

        Args:
            service: Instance du service de monitoring temps réel.
        """
        try:
            # Récupération des données actuelles
            summary = service.get_system_summary()

            # Récupération des nouvelles alertes
            recent_alerts = service.alert_manager.alerts_history

            # Mise à jour thread-safe
            with self._lock:
                # Sauvegarde des anciennes données pour détecter les changements
                old_summary = self._last_summary
                self._last_summary = summary

                # Détection des nouvelles alertes
                new_alerts = []
                if len(recent_alerts) > len(self._last_alerts):
                    new_alerts = recent_alerts[len(self._last_alerts):]

                # Utiliser extend pour maintenir la deque avec limite
                self._last_alerts.clear()
                self._last_alerts.extend(recent_alerts)

                # Notification des callbacks pour les nouvelles alertes
                for alert in new_alerts:
                    for callback in self._alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            self._logger.error(f"Error in alert callback: {e}")

                # Notification des callbacks pour les nouvelles données
                # Vérifier si les données ont changé significativement
                if old_summary and ThreadSafeMonitoringService._has_significant_change(old_summary, summary):
                    for callback in self._data_callbacks:
                        try:
                            callback(summary)
                        except Exception as e:
                            self._logger.error(f"Error in data callback: {e}")

            # Ajout des données à la queue (non-bloquant)
            try:
                self._data_queue.put_nowait(summary)
            except queue.Full:
                # Queue pleine, on retire l'ancien élément
                try:
                    self._data_queue.get_nowait()
                    self._data_queue.put_nowait(summary)
                except queue.Empty:
                    pass

        except Exception as e:
            self._logger.error(f"Error updating cache: {e}")
    
    @staticmethod
    def _has_significant_change(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Détermine si les données ont changé de manière significative.
        
        Args:
            old_data: Anciennes données.
            new_data: Nouvelles données.
            
        Returns:
            True si les données ont changé de manière significative.
        """
        # Vérifier les changements dans les métriques clés
        thresholds = {
            'cpu_usage': CPU_USAGE_CHANGE_THRESHOLD,    # % de différence
            'memory_usage': MEMORY_USAGE_CHANGE_THRESHOLD, # % de différence
            'disk_usage': DISK_USAGE_CHANGE_THRESHOLD    # % de différence
        }
        
        for key, threshold in thresholds.items():
            old_val = old_data.get(key, 0)
            new_val = new_data.get(key, 0)
            if abs(new_val - old_val) > threshold:
                return True
        
        return False

    def __enter__(self) -> 'ThreadSafeMonitoringService':
        """Support du context manager."""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """Support du context manager."""
        self.stop()

    def __del__(self) -> None:
        """Nettoyage lors de la destruction."""
        if self._is_running:
            try:
                self.stop()
            except (RuntimeError, Exception):
                pass
