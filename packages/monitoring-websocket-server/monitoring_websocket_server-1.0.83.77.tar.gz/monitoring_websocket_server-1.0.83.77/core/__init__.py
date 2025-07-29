"""Module principal contenant les composants de base du système de monitoring.

Ce module fournit les modèles de données, énumérations et exceptions
utilisés dans tout le système de monitoring.

Classes de modèles:
    MemoryInfo: Informations sur l'utilisation de la mémoire
    ProcessorInfo: Informations sur l'utilisation du processeur
    DiskInfo: Informations sur l'utilisation du disque
    OSInfo: Informations sur le système d'exploitation
    MonitoringSnapshot: Snapshot complet de l'état du système
    Alert: Modèle pour les alertes système

Énumérations:
    AlertLevel: Niveaux d'alerte (INFO, WARNING, CRITICAL)
    MonitoringStatus: États du système de monitoring
    ComponentType: Types de composants monitorés

Exceptions:
    MonitoringError: Exception de base pour toutes les erreurs de monitoring
    MonitorInitializationError: Erreur d'initialisation d'un moniteur
    DataCollectionError: Erreur de collecte de données
    ServiceStartupError: Erreur de démarrage du service
    ServiceShutdownError: Erreur d'arrêt du service
    AlertConfigurationError: Erreur de configuration des alertes
    ExportError: Erreur d'export de données
    InvalidThresholdError: Seuil invalide
    InvalidIntervalError: Intervalle invalide
"""

from .models import (
    MemoryInfo,
    ProcessorInfo,
    DiskInfo,
    OSInfo,
    MonitoringSnapshot,
    Alert
)
from .enums import AlertLevel, MonitoringStatus, ComponentType
from .exceptions import (
    MonitoringError,
    MonitorInitializationError,
    DataCollectionError,
    ServiceStartupError,
    ServiceShutdownError,
    AlertConfigurationError,
    ExportError,
    InvalidThresholdError,
    InvalidIntervalError
)

__all__ = [
    # Models
    "MemoryInfo",
    "ProcessorInfo",
    "DiskInfo",
    "OSInfo",
    "MonitoringSnapshot",
    "Alert",
    # Enums
    "AlertLevel",
    "MonitoringStatus",
    "ComponentType",
    # Exceptions
    "MonitoringError",
    "MonitorInitializationError",
    "DataCollectionError",
    "ServiceStartupError",
    "ServiceShutdownError",
    "AlertConfigurationError",
    "ExportError",
    "InvalidThresholdError",
    "InvalidIntervalError"
]