"""
Factory pour la création de moniteurs système.
Facilite la création et configuration des différents types de moniteurs.
"""

from typing import Dict, Any, Type, List
from pathlib import Path

from .base import BaseMonitor
from .memory import MemoryMonitor
from .processor import ProcessorMonitor
from .disk import DiskMonitor
from .system import OSMonitor, SystemMonitor
from ..core.exceptions import MonitorInitializationError


class MonitorFactory:
    """Factory pour créer et configurer les moniteurs système.

    Centralise la logique de création et permet une configuration
    flexible selon les besoins de l'application.
    """

    # Mapping des types de moniteurs disponibles
    _MONITOR_CLASSES: Dict[str, Type[BaseMonitor]] = {
        "memory": MemoryMonitor,
        "processor": ProcessorMonitor,
        "disk": DiskMonitor,
        "os": OSMonitor
    }

    @classmethod
    def create_monitor(cls, monitor_type: str, **kwargs) -> BaseMonitor:
        """
        Crée un moniteur du type spécifié.

        Args:
            monitor_type (str): Type de moniteur à créer
            **kwargs: Arguments spécifiques au moniteur

        Returns:
            BaseMonitor: Instance du moniteur créé

        Raises:
            MonitorInitializationError: Si le type n'est pas supporté
        """
        if monitor_type not in cls._MONITOR_CLASSES:
            raise MonitorInitializationError(
                f"Type de moniteur non supporté: {monitor_type}. "
                f"Types disponibles: {list(cls._MONITOR_CLASSES.keys())}"
            )

        monitor_class = cls._MONITOR_CLASSES[monitor_type]
        
        try:
            return monitor_class(**kwargs)
        except Exception as e:
            raise MonitorInitializationError(
                f"Erreur lors de la création du moniteur {monitor_type}: {e}"
            )

    @classmethod
    def create_memory_monitor(cls) -> MemoryMonitor:
        """
        Crée un moniteur de mémoire avec configuration par défaut.

        Returns:
            MemoryMonitor: Moniteur de mémoire configuré
        """
        monitor = cls.create_monitor("memory")
        assert isinstance(monitor, MemoryMonitor)
        return monitor

    @classmethod
    def create_processor_monitor(cls, 
                               interval: float = 0.05,
                               max_errors: int = 10) -> ProcessorMonitor:
        """
        Crée un moniteur de processeur avec configuration personnalisée.

        Args:
            interval (float): Intervalle de mesure en secondes
            max_errors (int): Nombre maximum d'erreurs autorisées

        Returns:
            ProcessorMonitor: Moniteur de processeur configuré
        """
        monitor = cls.create_monitor("processor", interval=interval)
        assert isinstance(monitor, ProcessorMonitor)
        monitor.max_errors = max_errors
        return monitor

    @classmethod
    def create_disk_monitor(cls, 
                          path: str = "/",
                          max_errors: int = 10) -> DiskMonitor:
        """
        Crée un moniteur de disque avec configuration personnalisée.

        Args:
            path (str): Chemin du disque à surveiller
            max_errors (int): Nombre maximum d'erreurs autorisées

        Returns:
            DiskMonitor: Moniteur de disque configuré
        """
        monitor = cls.create_monitor("disk", path=path)
        assert isinstance(monitor, DiskMonitor)
        monitor.max_errors = max_errors
        return monitor

    @classmethod
    def create_os_monitor(cls) -> OSMonitor:
        """
        Crée un moniteur du système d'exploitation.

        Returns:
            OSMonitor: Moniteur OS configuré
        """
        monitor = cls.create_monitor("os")
        assert isinstance(monitor, OSMonitor)
        return monitor

    @classmethod
    def create_system_monitor(cls, 
                            processor_interval: float = 0.05,
                            disk_path: str = "/",
                            auto_initialize: bool = True) -> SystemMonitor:
        """
        Crée un moniteur système complet avec tous les sous-moniteurs.

        Args:
            processor_interval (float): Intervalle pour le moniteur processeur
            disk_path (str): Chemin pour le moniteur disque
            auto_initialize (bool): Initialiser automatiquement

        Returns:
            SystemMonitor: Moniteur système complet

        Raises:
            MonitorInitializationError: En cas d'erreur d'initialisation
        """
        try:
            monitor = SystemMonitor(
                processor_interval=processor_interval,
                disk_path=disk_path
            )
            
            if auto_initialize:
                monitor.initialize()
            
            return monitor
            
        except Exception as e:
            raise MonitorInitializationError(
                f"Erreur lors de la création du SystemMonitor: {e}"
            )

    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> SystemMonitor:
        """
        Crée un moniteur système à partir d'une configuration.

        Args:
            config (Dict[str, Any]): Configuration des moniteurs

        Returns:
            SystemMonitor: Moniteur système configuré

        Raises:
            MonitorInitializationError: En cas d'erreur de configuration

        Example:
            config = {
                "processor": {"interval": 0.1},
                "disk": {"path": "/home"},
                "auto_initialize": True
            }
        """
        try:
            # Configuration du processeur
            processor_config = config.get("processor", {})
            processor_interval = processor_config.get("interval", 0.05)

            # Configuration du disque
            disk_config = config.get("disk", {})
            disk_path = disk_config.get("path", "/")

            # Options générales
            auto_initialize = config.get("auto_initialize", True)

            return cls.create_system_monitor(
                processor_interval=processor_interval,
                disk_path=disk_path,
                auto_initialize=auto_initialize
            )

        except Exception as e:
            raise MonitorInitializationError(
                f"Erreur lors de la création depuis la configuration: {e}"
            )

    @classmethod
    def get_available_types(cls) -> List[str]:
        """
        Retourne la liste des types de moniteurs disponibles.

        Returns:
            list[str]: Types de moniteurs supportés
        """
        return list(cls._MONITOR_CLASSES.keys())

    @classmethod
    def validate_monitor_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide et normalise une configuration de moniteur.

        Args:
            config (Dict[str, Any]): Configuration à valider

        Returns:
            Dict[str, Any]: Configuration validée et normalisée

        Raises:
            ValueError: Si la configuration est invalide
        """
        validated_config = {}

        # Validation de la configuration processeur
        if "processor" in config:
            proc_config = config["processor"]
            if not isinstance(proc_config, dict):
                raise ValueError("La configuration 'processor' doit être un dictionnaire")
            
            interval = proc_config.get("interval", 0.05)
            if not isinstance(interval, (int, float)) or interval <= 0:
                raise ValueError("L'intervalle du processeur doit être un nombre positif")
            
            validated_config["processor"] = {"interval": float(interval)}

        # Validation de la configuration disque
        if "disk" in config:
            disk_config = config["disk"]
            if not isinstance(disk_config, dict):
                raise ValueError("La configuration 'disk' doit être un dictionnaire")
            
            path = disk_config.get("path", "/")
            if not isinstance(path, str):
                raise ValueError("Le chemin du disque doit être une chaîne")
            
            # Vérification que le chemin existe
            path_obj = Path(path)
            if not path_obj.exists():
                raise ValueError(f"Le chemin {path} n'existe pas")
            
            validated_config["disk"] = {"path": path}

        # Validation des options générales
        auto_init = config.get("auto_initialize", True)
        if not isinstance(auto_init, bool):
            raise ValueError("'auto_initialize' doit être un booléen")
        
        validated_config["auto_initialize"] = auto_init

        return validated_config

    @classmethod
    def create_monitoring_preset(cls, preset_name: str) -> SystemMonitor:
        """
        Crée un moniteur système avec une configuration prédéfinie.

        Args:
            preset_name (str): Nom du preset à utiliser

        Returns:
            SystemMonitor: Moniteur système configuré

        Raises:
            ValueError: Si le preset n'existe pas
        """
        presets = {
            "default": {
                "processor": {"interval": 0.05},
                "disk": {"path": "/"},
                "auto_initialize": True
            },
            "fast_monitoring": {
                "processor": {"interval": 0.01},
                "disk": {"path": "/"},
                "auto_initialize": True
            },
            "low_resource": {
                "processor": {"interval": 0.5},
                "disk": {"path": "/"},
                "auto_initialize": True
            },
            "server_monitoring": {
                "processor": {"interval": 0.1},
                "disk": {"path": "/"},
                "auto_initialize": True
            }
        }

        if preset_name not in presets:
            available_presets = list(presets.keys())
            raise ValueError(
                f"Preset '{preset_name}' non trouvé. "
                f"Presets disponibles: {available_presets}"
            )

        return cls.create_from_config(presets[preset_name])

    @classmethod
    def get_preset_descriptions(cls) -> Dict[str, str]:
        """
        Retourne les descriptions des presets disponibles.

        Returns:
            Dict[str, str]: Descriptions des presets
        """
        return {
            "default": "Configuration par défaut équilibrée",
            "fast_monitoring": "Monitoring très fréquent pour applications critiques",
            "low_resource": "Configuration économe en ressources",
            "server_monitoring": "Optimisé pour la surveillance de serveurs"
        }


class MonitorBuilder:
    """Builder pattern pour une construction fluide des moniteurs.

    Permet une configuration étape par étape avec validation.
    """

    def __init__(self) -> None:
        """Initialise le builder."""
        self._config: Dict[str, Any] = {}

    def with_processor_interval(self, interval: float) -> 'MonitorBuilder':
        """
        Configure l'intervalle du moniteur processeur.

        Args:
            interval (float): Intervalle en secondes

        Returns:
            MonitorBuilder: Instance du builder pour chaînage
        """
        if "processor" not in self._config:
            self._config["processor"] = {}
        self._config["processor"]["interval"] = interval
        return self

    def with_disk_path(self, path: str) -> 'MonitorBuilder':
        """
        Configure le chemin du moniteur disque.

        Args:
            path (str): Chemin du disque

        Returns:
            MonitorBuilder: Instance du builder pour chaînage
        """
        if "disk" not in self._config:
            self._config["disk"] = {}
        self._config["disk"]["path"] = path
        return self

    def with_auto_initialization(self, auto_init: bool = True) -> 'MonitorBuilder':
        """
        Configure l'initialisation automatique.

        Args:
            auto_init (bool): Activer l'initialisation automatique

        Returns:
            MonitorBuilder: Instance du builder pour chaînage
        """
        self._config["auto_initialize"] = auto_init
        return self

    def build(self) -> SystemMonitor:
        """
        Construit le moniteur système avec la configuration actuelle.

        Returns:
            SystemMonitor: Moniteur système configuré

        Raises:
            MonitorInitializationError: En cas d'erreur de construction
        """
        validated_config = MonitorFactory.validate_monitor_config(self._config)
        return MonitorFactory.create_from_config(validated_config)

    def reset(self) -> 'MonitorBuilder':
        """
        Remet à zéro la configuration.

        Returns:
            MonitorBuilder: Instance du builder réinitialisée
        """
        self._config.clear()
        return self
