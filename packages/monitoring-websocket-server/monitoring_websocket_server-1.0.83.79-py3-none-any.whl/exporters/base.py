"""Classe de base pour tous les exporteurs de données.

Définit l'interface commune et les fonctionnalités partagées pour
l'export des données de monitoring dans différents formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List

from ..core.models import MonitoringSnapshot
from ..core.exceptions import ExportError


class BaseExporter(ABC):
    """Classe abstraite de base pour tous les exporteurs de données.
    
    Définit l'interface commune que tous les exporteurs doivent implémenter
    et fournit des fonctionnalités de base pour la gestion des répertoires
    et la validation des données.
    """

    def __init__(self, output_dir: Path) -> None:
        """Initialise l'exporteur de base.

        Args:
            output_dir: Répertoire de sortie pour les exports.

        Raises:
            ExportError: Si le répertoire ne peut pas être créé.
        """
        self._output_dir: Path = Path(output_dir)
        self._ensure_output_directory()

    @property
    def output_dir(self) -> Path:
        """Retourne le répertoire de sortie.

        Returns:
            Le répertoire de sortie configuré.
        """
        return self._output_dir

    @output_dir.setter
    def output_dir(self, new_dir: Path) -> None:
        """Définit un nouveau répertoire de sortie.

        Args:
            new_dir: Nouveau répertoire de sortie.

        Raises:
            ExportError: Si le répertoire ne peut pas être créé.
        """
        self._output_dir = Path(new_dir)
        self._ensure_output_directory()

    def _ensure_output_directory(self) -> None:
        """S'assure que le répertoire de sortie existe.

        Crée le répertoire et tous ses parents si nécessaire.

        Raises:
            ExportError: Si le répertoire ne peut pas être créé.
        """
        try:
            self._output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ExportError(f"Impossible de créer le répertoire de sortie {self._output_dir}: {e}")

    @staticmethod
    def validate_snapshot(snapshot: MonitoringSnapshot) -> None:
        """Valide un snapshot avant export.

        Vérifie que toutes les informations requises sont présentes
        dans le snapshot avant de procéder à l'export.

        Args:
            snapshot: Snapshot à valider.

        Raises:
            ExportError: Si le snapshot est invalide ou incomplet.
        """
        if snapshot is None:
            raise ExportError("Le snapshot ne peut pas être None")
        
        if snapshot.timestamp is None:
            raise ExportError("Le timestamp du snapshot ne peut pas être None")
        
        if not hasattr(snapshot, 'memory_info') or snapshot.memory_info is None:
            raise ExportError("Les informations mémoire sont requises")
        
        if not hasattr(snapshot, 'processor_info') or snapshot.processor_info is None:
            raise ExportError("Les informations processeur sont requises")
        
        if not hasattr(snapshot, 'disk_info') or snapshot.disk_info is None:
            raise ExportError("Les informations disque sont requises")

    def get_file_size(self, filename: str) -> int:
        """Retourne la taille d'un fichier exporté.

        Args:
            filename: Nom du fichier.

        Returns:
            La taille du fichier en bytes.

        Raises:
            ExportError: Si le fichier n'existe pas.
        """
        filepath = self._output_dir / filename
        if not filepath.exists():
            raise ExportError(f"Le fichier {filename} n'existe pas")
        
        return filepath.stat().st_size

    def list_exported_files(self) -> List[Path]:
        """Liste tous les fichiers exportés dans le répertoire.

        Returns:
            Liste des chemins des fichiers exportés. Retourne une liste
            vide en cas d'erreur d'accès au répertoire.
        """
        try:
            return list(self._output_dir.iterdir())
        except (OSError, IOError, PermissionError):
            return []

    def cleanup_old_files(self, max_files: int = 10) -> int:
        """Supprime les anciens fichiers exportés.

        Conserve uniquement les fichiers les plus récents selon la
        limite spécifiée.

        Args:
            max_files: Nombre maximum de fichiers à conserver.
                Par défaut: 10.

        Returns:
            Le nombre de fichiers supprimés.
        """
        files = sorted(self.list_exported_files(), key=lambda f: f.stat().st_mtime, reverse=True)
        files_to_delete = files[max_files:]
        
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
            except (OSError, IOError, PermissionError):
                continue  # Ignore les erreurs de suppression
        
        return deleted_count

    def get_export_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'export.

        Calcule et retourne diverses statistiques sur les fichiers
        exportés dans le répertoire de sortie.

        Returns:
            Dictionnaire contenant:
            - file_count: Nombre de fichiers
            - total_size_bytes: Taille totale en bytes
            - total_size_mb: Taille totale en MB
            - output_directory: Chemin du répertoire
            - directory_exists: État d'existence du répertoire
        """
        files = self.list_exported_files()
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            "file_count": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "output_directory": str(self._output_dir),
            "directory_exists": self._output_dir.exists()
        }

    @abstractmethod
    async def export_snapshot(self, snapshot: MonitoringSnapshot) -> None:
        """Exporte un instantané de données.

        Méthode abstraite à implémenter par les sous-classes pour
        réaliser l'export dans le format spécifique.

        Args:
            snapshot: Données de monitoring à exporter.

        Raises:
            ExportError: En cas d'erreur durant l'export.
        """
        pass

    def __str__(self) -> str:
        """Représentation textuelle de l'exporteur.

        Returns:
            Description lisible de l'exporteur avec son répertoire.
        """
        return f"{self.__class__.__name__}(output_dir='{self._output_dir}')"

    def __repr__(self) -> str:
        """Représentation technique de l'exporteur.

        Returns:
            Représentation technique pour le débogage.
        """
        return f"{self.__class__.__name__}(output_dir=Path('{self._output_dir}'))"
