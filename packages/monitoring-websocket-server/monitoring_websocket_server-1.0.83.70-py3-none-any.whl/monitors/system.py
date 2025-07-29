"""
Moniteurs système et OS.
Surveillance des informations du système d'exploitation et coordination des moniteurs.
"""

import time
import platform
import logging
import socket
from typing import Optional, Dict, Any

from .base import BaseMonitor
from .memory import MemoryMonitor
from .processor import ProcessorMonitor
from .disk import DiskMonitor
from ..core.models import OSInfo


class OSMonitor(BaseMonitor):
    """Moniteur pour surveiller les informations du système d'exploitation."""

    def __init__(self) -> None:
        """Initialiser le moniteur du système d'exploitation."""
        super().__init__("OS")
        self._os_info: Optional[OSInfo] = None

    @property
    def os_info(self) -> Optional[OSInfo]:
        """Retourner les informations OS en cache.

        Returns:
            Informations OS ou None si pas encore récupérées.
        """
        return self._os_info

    def _do_initialize(self) -> None:
        """Initialiser le moniteur OS.

        Raises:
            Exception: Si les informations système ne sont pas accessibles.
        """
        try:
            # Test d'accès aux informations système
            platform.system()
            platform.version()
            
            # Collecter les informations OS une seule fois à l'initialisation
            # car elles ne changent jamais pendant l'exécution
            self._collect_and_cache_os_info()
            
        except Exception as e:
            raise Exception(f"Impossible d'accéder aux informations système: {e}")

    def _collect_data(self) -> OSInfo:
        """Retourner les informations du système d'exploitation depuis le cache.

        Returns:
            Informations complètes sur le système d'exploitation.

        Raises:
            Exception: Si les informations OS n'ont pas été initialisées.
        """
        if self._os_info is None:
            raise Exception("Les informations OS n'ont pas été initialisées correctement")
        
        # Retourner une copie avec un timestamp mis à jour
        # pour maintenir la compatibilité avec le reste du système
        return OSInfo(
            name=self._os_info.name,
            version=self._os_info.version,
            release=self._os_info.release,
            architecture=self._os_info.architecture,
            machine=self._os_info.machine,
            processor=self._os_info.processor,
            platform=self._os_info.platform,
            python_version=self._os_info.python_version,
            hostname=self._os_info.hostname,
            timestamp=time.time()
        )
    
    def _collect_and_cache_os_info(self) -> None:
        """Collecter et mettre en cache les informations OS une seule fois.

        Cette méthode est appelée uniquement lors de l'initialisation.
        """
        try:
            self._os_info = OSInfo(
                name=platform.system(),
                version=platform.version(),
                release=platform.release(),
                architecture=platform.architecture()[0],
                machine=platform.machine(),
                processor=platform.processor() or "Unknown",
                platform=platform.platform(),
                python_version=platform.python_version(),
                hostname=socket.gethostname(),
                timestamp=time.time()
            )
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des informations OS: {e}")

    def get_os_info(self) -> OSInfo:
        """Récupérer les informations du système d'exploitation.

        Méthode publique pour compatibilité avec l'ancien code.

        Returns:
            Informations complètes sur le système d'exploitation.
        """
        return self.get_data()

    def is_windows(self) -> bool:
        """Vérifier si le système est Windows.

        Returns:
            True si Windows.
        """
        os_info = self.get_data()
        return os_info.name.lower() == "windows"

    def is_linux(self) -> bool:
        """Vérifier si le système est Linux.

        Returns:
            True si Linux.
        """
        os_info = self.get_data()
        return os_info.name.lower() == "linux"

    def is_macos(self) -> bool:
        """Vérifier si le système est macOS.

        Returns:
            True si macOS.
        """
        os_info = self.get_data()
        return os_info.name.lower() == "darwin"

    def get_architecture(self) -> str:
        """Récupérer l'architecture du système.

        Returns:
            Architecture (64bit, 32bit, etc.).
        """
        os_info = self.get_data()
        return os_info.architecture

    def get_platform_summary(self) -> Dict[str, Any]:
        """Retourner un résumé des informations de plateforme.

        Returns:
            Résumé de la plateforme.
        """
        os_info = self.get_data()
        
        return {
            "system": os_info.name,
            "release": os_info.release,
            "version": os_info.version,
            "architecture": os_info.architecture,
            "machine": os_info.machine,
            "python_version": os_info.python_version,
            "is_64bit": "64" in os_info.architecture,
            "platform_string": os_info.platform
        }


class SystemMonitor:
    """Moniteur système principal qui coordonne tous les sous-moniteurs."""

    def __init__(self, 
                 processor_interval: float = 0.05,
                 disk_path: str = "/") -> None:
        """Initialiser le moniteur système complet.

        Args:
            processor_interval: Intervalle pour le moniteur processeur.
            disk_path: Chemin pour le moniteur disque.
        """
        self._memory_monitor: MemoryMonitor = MemoryMonitor()
        self._processor_monitor: ProcessorMonitor = ProcessorMonitor(processor_interval)
        self._disk_monitor: DiskMonitor = DiskMonitor(disk_path)
        self._os_monitor: OSMonitor = OSMonitor()
        
        # Essayer d'initialiser le moniteur GPU
        try:
            from .gpu import GPUMonitor as GPUMonitorClass
            self._gpu_monitor: Optional[GPUMonitorClass] = GPUMonitorClass()
        except ImportError:
            from .gpu import GPUMonitor as GPUMonitorClass
            self._gpu_monitor = None
        
        self._initialized: bool = False
        self._logger: logging.Logger = logging.getLogger(__name__)

    @property
    def memory_monitor(self) -> MemoryMonitor:
        """Retourner le moniteur mémoire.

        Returns:
            Moniteur de mémoire.
        """
        return self._memory_monitor

    @property
    def processor_monitor(self) -> ProcessorMonitor:
        """Retourner le moniteur processeur.

        Returns:
            Moniteur de processeur.
        """
        return self._processor_monitor

    @property
    def disk_monitor(self) -> DiskMonitor:
        """Retourner le moniteur disque.

        Returns:
            Moniteur de disque.
        """
        return self._disk_monitor

    @property
    def os_monitor(self) -> OSMonitor:
        """Retourner le moniteur du système d'exploitation.

        Returns:
            Moniteur OS.
        """
        return self._os_monitor

    @property
    def initialized(self) -> bool:
        """Indiquer si le système de monitoring est initialisé.

        Returns:
            True si initialisé.
        """
        return self._initialized

    def initialize(self) -> None:
        """Initialiser tous les moniteurs.

        Raises:
            Exception: En cas d'erreur d'initialisation.
        """
        try:
            self._memory_monitor.initialize()
            self._processor_monitor.initialize()
            self._disk_monitor.initialize()
            self._os_monitor.initialize()
            
            # Initialiser GPU si disponible
            if self._gpu_monitor:
                try:
                    self._gpu_monitor.initialize()
                except Exception as e:
                    # Ne pas échouer si GPU non disponible
                    print(f"GPU monitoring non disponible: {e}")
                    self._gpu_monitor = None
                    
            self._initialized = True
        except Exception as e:
            raise Exception(f"Erreur lors de l'initialisation du système de monitoring: {e}")

    def get_all_data(self) -> Dict[str, Any]:
        """Récupérer toutes les données de tous les moniteurs.

        Returns:
            Dictionnaire avec toutes les données.

        Raises:
            Exception: En cas d'erreur de collecte.
        """
        if not self._initialized:
            self.initialize()

        data = {
            "memory": self._memory_monitor.get_data(),
            "processor": self._processor_monitor.get_data(),
            "disk": self._disk_monitor.get_data(),
            "os": self._os_monitor.get_data(),
            "timestamp": time.time()
        }
        
        # Ajouter GPU si disponible
        if self._gpu_monitor:
            try:
                data["gpu"] = self._gpu_monitor.get_data()
            except (AttributeError, RuntimeError, ValueError, Exception) as e:
                self._logger.debug(f"Erreur lors de la collecte des données GPU: {e}")
                data["gpu"] = None
                
        return data

    def get_health_status(self) -> Dict[str, Any]:
        """Retourner le statut de santé de tous les moniteurs.

        Returns:
            Statut de santé global.
        """
        return {
            "memory": self._memory_monitor.get_status(),
            "processor": self._processor_monitor.get_status(),
            "disk": self._disk_monitor.get_status(),
            "os": self._os_monitor.get_status(),
            "system_healthy": self.is_healthy()
        }

    def is_healthy(self) -> bool:
        """Vérifier si tous les moniteurs sont en bonne santé.

        Returns:
            True si tous les moniteurs fonctionnent.
        """
        return (self._memory_monitor.is_healthy() and
                self._processor_monitor.is_healthy() and
                self._disk_monitor.is_healthy() and
                self._os_monitor.is_healthy())

    def reset_all_errors(self) -> None:
        """Remettre à zéro les compteurs d'erreur de tous les moniteurs."""
        self._memory_monitor.reset_errors()
        self._processor_monitor.reset_errors()
        self._disk_monitor.reset_errors()
        self._os_monitor.reset_errors()

    def configure_processor_interval(self, interval: float) -> None:
        """Configurer l'intervalle du moniteur processeur.

        Args:
            interval: Nouvel intervalle.
        """
        self._processor_monitor.interval = interval

    def configure_disk_path(self, path: str) -> None:
        """Configurer le chemin du moniteur disque.

        Args:
            path: Nouveau chemin.
        """
        self._disk_monitor.path = path

    def get_quick_summary(self) -> Dict[str, Any]:
        """Retourner un résumé rapide des métriques principales.

        Returns:
            Résumé des métriques clés.
        """
        try:
            return {
                "memory_percent": self._memory_monitor.get_usage_percentage(),
                "cpu_percent": self._processor_monitor.get_usage_percentage(),
                "disk_percent": self._disk_monitor.get_usage_percentage(),
                "system_healthy": self.is_healthy(),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "error": str(e),
                "system_healthy": False,
                "timestamp": time.time()
            }
