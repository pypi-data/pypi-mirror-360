"""
Moniteur de mémoire système.
Surveillance de l'utilisation de la mémoire RAM.
"""

import time
from typing import Optional

import psutil

from ..config import MEMORY_WARNING_THRESHOLD, MEMORY_CRITICAL_THRESHOLD
from .base import BaseMonitor
from ..core.models import MemoryInfo


class MemoryMonitor(BaseMonitor):
    """Moniteur pour surveiller l'utilisation de la mémoire RAM."""

    def __init__(self) -> None:
        """Initialiser le moniteur de mémoire."""
        super().__init__("Memory")
        self._last_check: Optional[MemoryInfo] = None

    @property
    def last_check(self) -> Optional[MemoryInfo]:
        """Retourner les dernières informations mémoire récupérées.

        Returns:
            Dernières informations mémoire ou None.
        """
        return self._last_check

    def _do_initialize(self) -> None:
        """Initialiser le moniteur de mémoire.

        Raises:
            Exception: Si psutil n'est pas disponible.
        """
        # Test de disponibilité de psutil
        try:
            psutil.virtual_memory()
        except Exception as e:
            raise Exception(f"Impossible d'accéder aux informations mémoire: {e}")

    def _collect_data(self) -> MemoryInfo:
        """Collecter les informations actuelles sur la mémoire RAM.

        Returns:
            Informations détaillées sur la mémoire.

        Raises:
            Exception: En cas d'erreur de collecte.
        """
        current_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des données mémoire: {e}")

        memory_info = MemoryInfo(
            total=memory.total,
            available=memory.available,
            used=memory.used,
            percentage=memory.percent,
            timestamp=current_time
        )

        self._last_check = memory_info
        return memory_info

    def get_memory_info(self) -> MemoryInfo:
        """Récupérer les informations actuelles sur la mémoire RAM.

        Méthode publique pour compatibilité avec l'ancien code.

        Returns:
            Informations détaillées sur la mémoire.
        """
        return self.get_data()

    def get_usage_percentage(self) -> float:
        """Récupérer uniquement le pourcentage d'utilisation mémoire.

        Returns:
            Pourcentage d'utilisation.
        """
        memory_info = self.get_data()
        return memory_info.percentage

    def get_available_gb(self) -> float:
        """Récupérer la mémoire disponible en GB.

        Returns:
            Mémoire disponible en GB.
        """
        memory_info = self.get_data()
        return memory_info.available / (1024 ** 3)

    def get_used_gb(self) -> float:
        """Récupérer la mémoire utilisée en GB.

        Returns:
            Mémoire utilisée en GB.
        """
        memory_info = self.get_data()
        return memory_info.used / (1024 ** 3)

    def get_total_gb(self) -> float:
        """Récupérer la mémoire totale en GB.

        Returns:
            Mémoire totale en GB.
        """
        memory_info = self.get_data()
        return memory_info.total / (1024 ** 3)

    def is_memory_critical(self, threshold: float = MEMORY_CRITICAL_THRESHOLD) -> bool:
        """Vérifier si l'utilisation mémoire est critique.

        Args:
            threshold: Seuil critique en pourcentage.

        Returns:
            True si critique.
        """
        return self.get_usage_percentage() > threshold

    def is_memory_warning(self, threshold: float = MEMORY_WARNING_THRESHOLD) -> bool:
        """Vérifier si l'utilisation mémoire nécessite une alerte.

        Args:
            threshold: Seuil d'alerte en pourcentage.

        Returns:
            True si alerte nécessaire.
        """
        return self.get_usage_percentage() > threshold
