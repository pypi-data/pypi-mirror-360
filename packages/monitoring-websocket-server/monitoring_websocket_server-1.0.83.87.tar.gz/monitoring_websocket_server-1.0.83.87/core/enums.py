"""Énumérations et constantes pour le système de monitoring.

Ce module définit toutes les énumérations utilisées dans le système
pour garantir la cohérence des valeurs et faciliter la maintenance.

Classes:
    AlertLevel: Niveaux de sévérité des alertes
    MonitoringStatus: États du service de monitoring
    ComponentType: Types de composants système surveillés
"""

from enum import Enum


class AlertLevel(Enum):
    """Niveaux de sévérité des alertes système.
    
    Les niveaux sont ordonnés par ordre croissant de sévérité.
    
    Attributes:
        INFO: Information simple, aucune action requise
        WARNING: Avertissement, surveillance recommandée
        CRITICAL: Critique, action immédiate requise
    """
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitoringStatus(Enum):
    """États du cycle de vie du service de monitoring.
    
    Définit les différents états possibles du service principal.
    
    Attributes:
        STOPPED: Service arrêté
        STARTING: Service en cours de démarrage
        RUNNING: Service en cours d'exécution
        STOPPING: Service en cours d'arrêt
        ERROR: Service en erreur
    """
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class ComponentType(Enum):
    """Types de composants système surveillés.
    
    Identifie les différents types de ressources monitorées.
    
    Attributes:
        MEMORY: Mémoire RAM et swap
        CPU: Processeur et utilisation des cores
        DISK: Espace disque et E/S
        NETWORK: Interfaces réseau (futur)
        SYSTEM: Informations système générales
    """
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    NETWORK = "network"
    SYSTEM = "system"
