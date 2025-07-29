"""
Moniteur de disque système.
Surveillance de l'utilisation de l'espace disque.
"""

import time
import platform
from typing import Optional, Dict, Any
from pathlib import Path

import psutil

from ..config import (
    DEFAULT_DISK_PATH, DISK_WARNING_THRESHOLD, DISK_CRITICAL_THRESHOLD,
    DISK_MIN_FREE_GB, DISK_WARNING_FREE_GB, DISK_CRITICAL_FREE_GB
)
from .base import BaseMonitor
from ..core.models import DiskInfo


class DiskMonitor(BaseMonitor):
    """Moniteur pour surveiller l'utilisation du disque dur."""

    def __init__(self, path: str = DEFAULT_DISK_PATH) -> None:
        """Initialiser le moniteur de disque.

        Args:
            path: Chemin du disque à surveiller.
        """
        super().__init__("Disk")
        self._path: str = self._normalize_path(path)
        self._last_check: Optional[DiskInfo] = None

    @property
    def path(self) -> str:
        """Retourner le chemin surveillé.

        Returns:
            Chemin du disque surveillé.
        """
        return self._path

    @path.setter
    def path(self, new_path: str) -> None:
        """Définir le chemin à surveiller.

        Args:
            new_path: Nouveau chemin du disque.
        """
        self._path = self._normalize_path(new_path)
        self._last_check = None
        # Réinitialiser pour valider le nouveau chemin
        self._initialized = False

    @property
    def last_check(self) -> Optional[DiskInfo]:
        """Retourner les dernières informations disque récupérées.

        Returns:
            Dernières informations disque ou None.
        """
        return self._last_check

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normaliser le chemin selon la plateforme.

        Args:
            path: Chemin à normaliser.

        Returns:
            Chemin normalisé.
        """
        if path == "/" and platform.system().lower() == "windows":
            return "C:\\"
        return path

    def _do_initialize(self) -> None:
        """Initialiser le moniteur de disque.

        Raises:
            Exception: Si le chemin n'est pas accessible.
        """
        try:
            # Vérifier que le chemin existe et est accessible
            path_obj = Path(self._path)
            if not path_obj.exists():
                raise Exception(f"Le chemin {self._path} n'existe pas")
            
            # Test d'accès aux informations disque
            psutil.disk_usage(self._path)
        except Exception as e:
            raise Exception(f"Impossible d'accéder aux informations disque pour {self._path}: {e}")

    def _collect_data(self) -> DiskInfo:
        """Collecter les informations actuelles sur le disque.

        Returns:
            Informations détaillées sur le disque.

        Raises:
            Exception: En cas d'erreur de collecte.
        """
        current_time = time.time()
        
        try:
            disk_usage = psutil.disk_usage(self._path)
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des données disque: {e}")

        disk_info = DiskInfo(
            total=disk_usage.total,
            used=disk_usage.used,
            free=disk_usage.free,
            percentage=(disk_usage.used / disk_usage.total * 100) if disk_usage.total > 0 else 0.0,
            path=self._path,
            timestamp=current_time
        )

        self._last_check = disk_info
        return disk_info

    def get_disk_info(self) -> DiskInfo:
        """Récupérer les informations actuelles sur le disque.

        Méthode publique pour compatibilité avec l'ancien code.

        Returns:
            Informations détaillées sur le disque.
        """
        return self.get_data()

    def get_usage_percentage(self) -> float:
        """Récupérer uniquement le pourcentage d'utilisation disque.

        Returns:
            Pourcentage d'utilisation.
        """
        disk_info = self.get_data()
        return disk_info.percentage

    def get_free_gb(self) -> float:
        """Récupérer l'espace libre en GB.

        Returns:
            Espace libre en GB.
        """
        disk_info = self.get_data()
        return disk_info.free / (1024 ** 3)

    def get_used_gb(self) -> float:
        """Récupérer l'espace utilisé en GB.

        Returns:
            Espace utilisé en GB.
        """
        disk_info = self.get_data()
        return disk_info.used / (1024 ** 3)

    def get_total_gb(self) -> float:
        """Récupérer l'espace total en GB.

        Returns:
            Espace total en GB.
        """
        disk_info = self.get_data()
        return disk_info.total / (1024 ** 3)

    def get_free_tb(self) -> float:
        """Récupérer l'espace libre en TB.

        Returns:
            Espace libre en TB.
        """
        disk_info = self.get_data()
        return disk_info.free / (1024 ** 4)

    def get_used_tb(self) -> float:
        """Récupérer l'espace utilisé en TB.

        Returns:
            Espace utilisé en TB.
        """
        disk_info = self.get_data()
        return disk_info.used / (1024 ** 4)

    def get_total_tb(self) -> float:
        """Récupérer l'espace total en TB.

        Returns:
            Espace total en TB.
        """
        disk_info = self.get_data()
        return disk_info.total / (1024 ** 4)

    def is_disk_critical(self, threshold: float = DISK_CRITICAL_THRESHOLD) -> bool:
        """Vérifier si l'utilisation disque est critique.

        Args:
            threshold: Seuil critique en pourcentage.

        Returns:
            True si critique.
        """
        return self.get_usage_percentage() > threshold

    def is_disk_warning(self, threshold: float = DISK_WARNING_THRESHOLD) -> bool:
        """Vérifier si l'utilisation disque nécessite une alerte.

        Args:
            threshold: Seuil d'alerte en pourcentage.

        Returns:
            True si alerte nécessaire.
        """
        return self.get_usage_percentage() > threshold

    def is_disk_nearly_full(self, min_free_gb: float = DISK_MIN_FREE_GB) -> bool:
        """Vérifier s'il reste peu d'espace libre.

        Args:
            min_free_gb: Espace libre minimum en GB.

        Returns:
            True si peu d'espace libre.
        """
        return self.get_free_gb() < min_free_gb

    def get_disk_health_status(self) -> Dict[str, Any]:
        """Retourner un statut de santé détaillé du disque.

        Returns:
            Statut de santé du disque.
        """
        disk_info = self.get_data()
        usage_percent = disk_info.percentage
        free_gb = self.get_free_gb()
        
        # Détermination du statut
        if usage_percent > DISK_CRITICAL_THRESHOLD or free_gb < DISK_CRITICAL_FREE_GB:
            status = "critical"
            message = "Espace disque critique"
        elif usage_percent > DISK_WARNING_THRESHOLD or free_gb < DISK_WARNING_FREE_GB:
            status = "warning"
            message = "Espace disque faible"
        else:
            status = "good"
            message = "Espace disque suffisant"
        
        return {
            "status": status,
            "message": message,
            "usage_percent": usage_percent,
            "free_gb": free_gb,
            "total_gb": self.get_total_gb(),
            "path": self._path
        }

    def estimate_days_until_full(self, usage_growth_per_day_gb: float) -> float:
        """Estimer le nombre de jours avant que le disque soit plein.

        Args:
            usage_growth_per_day_gb: Croissance d'utilisation par jour en GB.

        Returns:
            Nombre de jours estimés (infini si décroissance).
        """
        if usage_growth_per_day_gb <= 0:
            return float('inf')
        
        free_gb = self.get_free_gb()
        return free_gb / usage_growth_per_day_gb
