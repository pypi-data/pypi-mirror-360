"""Factory pour la création d'exporteurs de données.

Facilite la création et configuration des différents types d'exporteurs
en centralisant la logique de construction et les configurations.
"""

import logging
from typing import Dict, Any, Type, Union, List
from pathlib import Path

from ..config import DEFAULT_EXPORT_DIR
from .base import BaseExporter
from .json_exporter import JSONExporter
from ..core.exceptions import ExportError


class ExporterFactory:
    """Factory pour créer et configurer les exporteurs de données.
    
    Centralise la logique de création et permet une configuration
    flexible selon les besoins de l'application.
    """

    # Logger de classe
    _logger: logging.Logger = logging.getLogger(__name__)

    # Mapping des types d'exporteurs disponibles
    _EXPORTER_CLASSES: Dict[str, Type[BaseExporter]] = {
        "json": JSONExporter,
        # Facilement extensible pour d'autres formats
        # "csv": CSVExporter,
        # "xml": XMLExporter,
        # "sqlite": SQLiteExporter,
    }

    @classmethod
    def create_exporter(cls, exporter_type: str, output_dir: Union[str, Path], 
                       **kwargs) -> BaseExporter:
        """Crée un exporteur du type spécifié.

        Args:
            exporter_type: Type d'exporteur à créer.
            output_dir: Répertoire de sortie.
            **kwargs: Arguments spécifiques à l'exporteur.

        Returns:
            Instance de l'exporteur créé.

        Raises:
            ExportError: Si le type n'est pas supporté.
        """
        if exporter_type not in cls._EXPORTER_CLASSES:
            raise ExportError(
                f"Unsupported exporter type: {exporter_type}. "
                f"Available types: {list(cls._EXPORTER_CLASSES.keys())}"
            )

        exporter_class = cls._EXPORTER_CLASSES[exporter_type]
        output_path = Path(output_dir) if isinstance(output_dir, str) else output_dir
        
        try:
            # JSONExporter accepte des paramètres supplémentaires
            if exporter_type == "json":
                # Création directe de JSONExporter avec les paramètres
                return JSONExporter(
                    output_path,
                    compress=kwargs.get('compress', False),
                    pretty_print=kwargs.get('pretty_print', True),
                    date_in_filename=kwargs.get('date_in_filename', True)
                )
            else:
                # Pour les autres exporteurs, on ne passe que output_path
                if kwargs:
                    cls._logger.warning(
                        f"Ignored parameters for {exporter_type}: {list(kwargs.keys())}"
                    )
                return exporter_class(output_path)
        except Exception as e:
            raise ExportError(
                f"Error creating exporter {exporter_type}: {e}"
            )

    @classmethod
    def create_json_exporter(cls, 
                           output_dir: Union[str, Path],
                           compress: bool = False,
                           pretty_print: bool = True,
                           date_in_filename: bool = True) -> JSONExporter:
        """Crée un exporteur JSON avec configuration personnalisée.

        Méthode de convenance pour créer rapidement un exporteur JSON
        avec des paramètres spécifiques.

        Args:
            output_dir: Répertoire de sortie.
            compress: Activer la compression gzip. Par défaut: False.
            pretty_print: Formater le JSON avec indentation. Par défaut: True.
            date_in_filename: Inclure la date dans le nom de fichier.
                Par défaut: True.

        Returns:
            Exporteur JSON configuré.
        """
        exporter = cls.create_exporter(
            "json",
            output_dir,
            compress=compress,
            pretty_print=pretty_print,
            date_in_filename=date_in_filename
        )
        # Cast explicite pour l'analyse de type
        assert isinstance(exporter, JSONExporter)
        return exporter

    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> BaseExporter:
        """Crée un exporteur à partir d'une configuration.

        Args:
            config: Configuration de l'exporteur contenant au minimum
                le type et optionnellement le répertoire de sortie.

        Returns:
            Exporteur configuré selon les paramètres fournis.

        Raises:
            ExportError: En cas d'erreur de configuration.

        Example:
            >>> config = {
            ...     "type": "json",
            ...     "output_dir": "./exports",
            ...     "compress": True,
            ...     "pretty_print": False
            ... }
            >>> exporter = ExporterFactory.create_from_config(config)
        """
        try:
            exporter_type = config.get("type", "json")
            output_dir = config.get("output_dir", DEFAULT_EXPORT_DIR)
            
            # Extraction des paramètres spécifiques
            specific_params = {k: v for k, v in config.items() 
                             if k not in ["type", "output_dir"]}
            
            return cls.create_exporter(exporter_type, output_dir, **specific_params)

        except Exception as e:
            raise ExportError(
                f"Error creating from configuration: {e}"
            )

    @classmethod
    def get_available_types(cls) -> List[str]:
        """Retourne la liste des types d'exporteurs disponibles.

        Returns:
            Liste des types d'exporteurs supportés.
        """
        return list(cls._EXPORTER_CLASSES.keys())

    @classmethod
    def validate_exporter_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et normalise une configuration d'exporteur.

        Vérifie la validité des paramètres et applique les valeurs
        par défaut si nécessaire.

        Args:
            config: Configuration à valider.

        Returns:
            Configuration validée et normalisée.

        Raises:
            ValueError: Si la configuration est invalide.
        """
        validated_config = {}

        # Validation du type
        exporter_type = config.get("type", "json")
        if exporter_type not in cls._EXPORTER_CLASSES:
            raise ValueError(
                f"Invalid exporter type: {exporter_type}. "
                f"Available types: {list(cls._EXPORTER_CLASSES.keys())}"
            )
        validated_config["type"] = exporter_type

        # Validation du répertoire de sortie
        output_dir = config.get("output_dir", DEFAULT_EXPORT_DIR)
        if not isinstance(output_dir, (str, Path)):
            raise ValueError("output_dir must be a string or Path")
        
        output_path = Path(output_dir)
        validated_config["output_dir"] = str(output_path)

        # Validation spécifique pour JSON
        if exporter_type == "json":
            # Compression
            compress = config.get("compress", False)
            if not isinstance(compress, bool):
                raise ValueError("compress must be a boolean")
            validated_config["compress"] = compress

            # Pretty print
            pretty_print = config.get("pretty_print", True)
            if not isinstance(pretty_print, bool):
                raise ValueError("pretty_print must be a boolean")
            validated_config["pretty_print"] = pretty_print

            # Date dans le nom de fichier
            date_in_filename = config.get("date_in_filename", True)
            if not isinstance(date_in_filename, bool):
                raise ValueError("date_in_filename must be a boolean")
            validated_config["date_in_filename"] = date_in_filename

        return validated_config

    @classmethod
    def create_export_preset(cls, preset_name: str, output_dir: Union[str, Path]) -> BaseExporter:
        """Crée un exporteur avec une configuration prédéfinie.

        Utilise un preset de configuration pour simplifier la création
        d'exporteurs avec des paramètres communs.

        Args:
            preset_name: Nom du preset à utiliser.
            output_dir: Répertoire de sortie.

        Returns:
            Exporteur configuré selon le preset.

        Raises:
            ValueError: Si le preset n'existe pas.
        """
        presets = {
            "default": {
                "type": "json",
                "compress": False,
                "pretty_print": True,
                "date_in_filename": True
            },
            "compressed": {
                "type": "json",
                "compress": True,
                "pretty_print": False,
                "date_in_filename": True
            },
            "development": {
                "type": "json",
                "compress": False,
                "pretty_print": True,
                "date_in_filename": False
            },
            "production": {
                "type": "json",
                "compress": True,
                "pretty_print": False,
                "date_in_filename": True
            },
            "minimal": {
                "type": "json",
                "compress": True,
                "pretty_print": False,
                "date_in_filename": False
            }
        }

        if preset_name not in presets:
            raise ValueError(
                f"Preset '{preset_name}' not found. "
                f"Available presets: {list(presets.keys())}"
            )

        config = presets[preset_name].copy()
        config["output_dir"] = output_dir
        return cls.create_from_config(config)

    @classmethod
    def get_preset_descriptions(cls) -> Dict[str, str]:
        """Retourne les descriptions des presets disponibles.

        Returns:
            Dictionnaire associant chaque nom de preset à sa description.
        """
        return {
            "default": "Default configuration with formatted JSON",
            "compressed": "Compressed files to save space",
            "development": "Optimized for development with readable JSON",
            "production": "Optimized for production with compression",
            "minimal": "Minimal configuration with maximum compression"
        }

    @classmethod
    def estimate_file_size(cls, exporter_type: str, data_points: int, 
                          compress: bool = False) -> Dict[str, float]:
        """Estime la taille des fichiers d'export.

        Calcule une estimation de la taille des fichiers qui seront
        générés selon le type d'exporteur et le nombre de données.

        Args:
            exporter_type: Type d'exporteur.
            data_points: Nombre de points de données à exporter.
            compress: Si la compression est activée. Par défaut: False.

        Returns:
            Dictionnaire contenant les estimations en:
            - bytes: Taille en octets
            - kb: Taille en kiloctets
            - mb: Taille en mégaoctets
            - gb: Taille en gigaoctets
            
        Raises:
            ValueError: Si le type d'exporteur n'est pas supporté.
        """
        # Estimation basée sur des moyennes observées
        base_sizes = {
            "json": 2048  # bytes par snapshot JSON
        }

        if exporter_type not in base_sizes:
            raise ValueError(f"Unsupported exporter type: {exporter_type}")

        base_size = base_sizes[exporter_type]
        total_bytes = base_size * data_points

        # Facteur de compression
        if compress:
            total_bytes *= 0.3  # Compression gzip ~70%

        return {
            "bytes": total_bytes,
            "kb": total_bytes / 1024,
            "mb": total_bytes / (1024 ** 2),
            "gb": total_bytes / (1024 ** 3)
        }


class ExporterBuilder:
    """Builder pattern pour une construction fluide des exporteurs.
    
    Permet une configuration étape par étape avec validation et
    offre une interface fluide pour la construction d'exporteurs.
    """

    def __init__(self) -> None:
        """Initialise le builder avec une configuration par défaut."""
        self._config: Dict[str, Any] = {
            "type": "json",
            "output_dir": DEFAULT_EXPORT_DIR
        }

    def of_type(self, exporter_type: str) -> 'ExporterBuilder':
        """Définit le type d'exporteur.

        Args:
            exporter_type: Type d'exporteur à utiliser.

        Returns:
            Instance du builder pour chaînage.
        """
        self._config["type"] = exporter_type
        return self

    def to_directory(self, output_dir: Union[str, Path]) -> 'ExporterBuilder':
        """Définit le répertoire de sortie.

        Args:
            output_dir: Répertoire de sortie pour les exports.

        Returns:
            Instance du builder pour chaînage.
        """
        self._config["output_dir"] = str(output_dir)
        return self

    def with_compression(self, enabled: bool = True) -> 'ExporterBuilder':
        """Configure la compression.

        Args:
            enabled: Activer la compression. Par défaut: True.

        Returns:
            Instance du builder pour chaînage.
        """
        self._config["compress"] = enabled
        return self

    def with_pretty_print(self, enabled: bool = True) -> 'ExporterBuilder':
        """Configure le formatage du JSON.

        Args:
            enabled: Activer le pretty-print. Par défaut: True.

        Returns:
            Instance du builder pour chaînage.
        """
        self._config["pretty_print"] = enabled
        return self

    def with_date_in_filename(self, enabled: bool = True) -> 'ExporterBuilder':
        """Configure l'inclusion de la date dans le nom de fichier.

        Args:
            enabled: Inclure la date. Par défaut: True.

        Returns:
            Instance du builder pour chaînage.
        """
        self._config["date_in_filename"] = enabled
        return self

    def build(self) -> BaseExporter:
        """Construit l'exporteur avec la configuration actuelle.

        Returns:
            Exporteur configuré selon les paramètres du builder.

        Raises:
            ExportError: En cas d'erreur de construction.
        """
        validated_config = ExporterFactory.validate_exporter_config(self._config)
        return ExporterFactory.create_from_config(validated_config)

    def reset(self) -> 'ExporterBuilder':
        """Remet à zéro la configuration.

        Réinitialise le builder avec les valeurs par défaut.

        Returns:
            Instance du builder réinitialisée.
        """
        self._config = {
            "type": "json",
            "output_dir": DEFAULT_EXPORT_DIR
        }
        return self

    def get_config(self) -> Dict[str, Any]:
        """Retourne la configuration actuelle.

        Returns:
            Copie de la configuration actuelle du builder.
        """
        return self._config.copy()
