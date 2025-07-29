"""Exporteur JSON pour les données de monitoring.

Gestion de l'export des données en format JSON avec compression
optionnelle et support de diverses options de formatage.
"""

import json
import gzip
import asyncio
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Any, Optional, List

from ..config import (
    EXPORT_COMPRESS_DEFAULT, EXPORT_PRETTY_PRINT_DEFAULT,
    EXPORT_DATE_IN_FILENAME_DEFAULT
)
from .base import BaseExporter
from ..core.models import MonitoringSnapshot, Alert
from ..core.exceptions import ExportError


class JSONExporter(BaseExporter):
    """Exporteur de données au format JSON.
    
    Permet l'export des snapshots de monitoring au format JSON avec
    support de la compression gzip et diverses options de formatage.
    """

    def __init__(self, 
                 output_dir: Path, 
                 compress: bool = EXPORT_COMPRESS_DEFAULT,
                 pretty_print: bool = EXPORT_PRETTY_PRINT_DEFAULT,
                 date_in_filename: bool = EXPORT_DATE_IN_FILENAME_DEFAULT) -> None:
        """Initialise l'exporteur JSON.

        Args:
            output_dir: Répertoire de sortie pour les exports.
            compress: Activer la compression gzip. Par défaut: False.
            pretty_print: Formater le JSON avec indentation. Par défaut: True.
            date_in_filename: Inclure la date dans le nom de fichier.
                Par défaut: True.
        """
        super().__init__(output_dir)
        self._compress: bool = compress
        self._pretty_print: bool = pretty_print
        self._date_in_filename: bool = date_in_filename

    @property
    def compress(self) -> bool:
        """Indique si la compression est activée.

        Returns:
            True si la compression gzip est activée.
        """
        return self._compress

    @compress.setter
    def compress(self, value: bool) -> None:
        """Active ou désactive la compression.

        Args:
            value: Nouvel état de compression.
        """
        self._compress = value

    @property
    def pretty_print(self) -> bool:
        """Indique si le formatage pretty-print est activé.

        Returns:
            True si le formatage avec indentation est activé.
        """
        return self._pretty_print

    @pretty_print.setter
    def pretty_print(self, value: bool) -> None:
        """Active ou désactive le pretty-print.

        Args:
            value: Nouvel état de pretty-print.
        """
        self._pretty_print = value

    def _generate_filename(self, snapshot: MonitoringSnapshot) -> str:
        """Génère le nom de fichier pour un snapshot.

        Args:
            snapshot: Snapshot à exporter.

        Returns:
            Nom de fichier généré avec l'extension appropriée.
        """
        base_name = "monitoring"
        
        if self._date_in_filename:
            date_str = snapshot.timestamp.strftime("%Y%m%d")
            base_name = f"monitoring_{date_str}"
        
        extension = ".json.gz" if self._compress else ".json"
        return base_name + extension

    def _prepare_data(self, snapshot: MonitoringSnapshot) -> Dict[str, Any]:
        """Prépare les données pour l'export.

        Convertit le snapshot en structure de données sérialisable
        avec métadonnées d'export.

        Args:
            snapshot: Snapshot à préparer.

        Returns:
            Structure de données prête pour la sérialisation JSON.
            
        Raises:
            ExportError: Si la préparation des données échoue.
        """
        try:
            # Conversion en dictionnaire avec gestion des types spéciaux
            data = {
                "export_info": {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "exporter": "JSONExporter",
                    "version": "1.0",
                    "compressed": self._compress
                },
                "monitoring_data": {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "memory": asdict(snapshot.memory_info),
                    "processor": asdict(snapshot.processor_info),
                    "disk": asdict(snapshot.disk_info),
                    "os": asdict(snapshot.os_info),
                    "alerts": [self._alert_to_dict(alert) for alert in snapshot.alerts]
                }
            }
            
            return data
            
        except Exception as e:
            raise ExportError(f"Erreur lors de la préparation des données: {e}")

    @staticmethod
    def _alert_to_dict(alert: Alert) -> Dict[str, Any]:
        """Convertit une alerte en dictionnaire.

        Args:
            alert: Alerte à convertir.

        Returns:
            Représentation dictionnaire de l'alerte avec types
            sérialisables.
        """
        alert_dict = asdict(alert)
        # Conversion de l'enum en string
        alert_dict['level'] = alert.level.value
        # Conversion du timestamp en ISO format
        alert_dict['timestamp'] = alert.timestamp.isoformat()
        return alert_dict

    async def export_snapshot(self, snapshot: MonitoringSnapshot) -> None:
        """Exporte un instantané vers un fichier JSON.

        Méthode asynchrone pour exporter un snapshot unique.

        Args:
            snapshot: Données de monitoring à exporter.

        Raises:
            ExportError: En cas d'erreur durant l'export.
        """
        try:
            filename = self._generate_filename(snapshot)
            filepath = self._output_dir / filename
            data = self._prepare_data(snapshot)

            # Export asynchrone
            await asyncio.get_event_loop().run_in_executor(
                None, self._write_file, filepath, data
            )
            
        except Exception as e:
            raise ExportError(f"Erreur lors de l'export JSON: {e}")

    def _write_file(self, filepath: Path, data: Dict[str, Any]) -> None:
        """Écrit un fichier JSON (avec compression optionnelle).

        Méthode interne pour l'écriture physique du fichier.

        Args:
            filepath: Chemin du fichier de sortie.
            data: Données à écrire.

        Raises:
            ExportError: En cas d'erreur d'écriture.
        """
        try:
            # Préparation des options JSON
            json_options: Dict[str, Any] = {
                "ensure_ascii": False,
                "default": str  # Conversion automatique des types non-sérialisables
            }
            
            if self._pretty_print:
                json_options["indent"] = 2
                json_options["separators"] = (",", ": ")

            # Écriture avec ou sans compression
            json_str = json.dumps(data, **json_options)
            
            if self._compress:
                with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                    f.write(json_str)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                    
        except Exception as e:
            raise ExportError(f"Erreur lors de l'écriture du fichier {filepath}: {e}")

    async def export_multiple_snapshots(self, snapshots: List[MonitoringSnapshot], filename: Optional[str] = None) -> None:
        """Exporte plusieurs snapshots dans un seul fichier.

        Permet l'export groupé de plusieurs snapshots pour optimiser
        l'espace disque et faciliter l'analyse historique.

        Args:
            snapshots: Liste des snapshots à exporter.
            filename: Nom de fichier personnalisé. Si None, un nom
                est généré automatiquement.

        Raises:
            ExportError: En cas d'erreur durant l'export.
        """
        if not snapshots:
            return

        try:
            # Génération du nom de fichier
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = f"monitoring_batch_{timestamp}"
                extension = ".json.gz" if self._compress else ".json"
                filename = base_name + extension

            filepath = self._output_dir / filename

            # Préparation des données groupées
            batch_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "exporter": "JSONExporter",
                    "version": "1.0",
                    "compressed": self._compress,
                    "count": len(snapshots),
                    "type": "batch_export"
                },
                "monitoring_data": [
                    self._prepare_data(snapshot)["monitoring_data"] 
                    for snapshot in snapshots
                ]
            }

            # Export asynchrone
            await asyncio.get_event_loop().run_in_executor(
                None, self._write_file, filepath, batch_data
            )
            
        except Exception as e:
            raise ExportError(f"Erreur lors de l'export batch JSON: {e}")

    def export_snapshot_sync(self, snapshot: MonitoringSnapshot) -> None:
        """Version synchrone de l'export (pour compatibilité).

        Méthode de compatibilité pour les contextes non-asynchrones.

        Args:
            snapshot: Données de monitoring à exporter.

        Raises:
            ExportError: En cas d'erreur durant l'export.
        """
        try:
            filename = self._generate_filename(snapshot)
            filepath = self._output_dir / filename
            data = self._prepare_data(snapshot)
            self._write_file(filepath, data)
        except Exception as e:
            raise ExportError(f"Erreur lors de l'export JSON synchrone: {e}")

    @staticmethod
    def load_snapshot(filepath: Path) -> Dict[str, Any]:
        """Charge un snapshot depuis un fichier JSON.

        Méthode statique pour relire les données exportées.

        Args:
            filepath: Chemin du fichier à charger.

        Returns:
            Données chargées depuis le fichier JSON.

        Raises:
            ExportError: Si le fichier n'existe pas ou en cas
                d'erreur de lecture/décodage.
        """
        try:
            if not filepath.exists():
                raise ExportError(f"Le fichier {filepath} n'existe pas")

            # Lecture avec ou sans décompression
            if filepath.suffix == '.gz':
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
            return data
            
        except json.JSONDecodeError as e:
            raise ExportError(f"Erreur de décodage JSON dans {filepath}: {e}")
        except Exception as e:
            raise ExportError(f"Erreur lors du chargement de {filepath}: {e}")

    def get_configuration(self) -> Dict[str, Any]:
        """Retourne la configuration actuelle de l'exporteur.

        Returns:
            Dictionnaire contenant tous les paramètres de configuration
            de l'exporteur JSON.
        """
        return {
            "type": "JSONExporter",
            "output_dir": str(self._output_dir),
            "compress": self._compress,
            "pretty_print": self._pretty_print,
            "date_in_filename": self._date_in_filename,
            "supported_extensions": [".json", ".json.gz"]
        }
