"""
Utilitaires système pour le monitoring.
Fonctions communes de formatage et de traitement des données système.
"""

from functools import lru_cache
from typing import Dict, Any
from datetime import datetime


class SystemUtils:
    """Utilitaires partagés pour le système de monitoring."""

    @staticmethod
    @lru_cache(maxsize=128)
    def format_bytes(byte_value: int) -> str:
        """Formate une valeur en bytes vers une unité lisible.

        Args:
            byte_value (int): Valeur en bytes à formater

        Returns:
            str: Valeur formatée avec l'unité appropriée
        """
        if byte_value == 0:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if byte_value < 1024.0:
                return f"{byte_value:.2f} {unit}"
            byte_value /= 1024.0
        return f"{byte_value:.2f} PB"

    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """Formate un pourcentage avec la précision donnée.

        Args:
            value (float): Valeur à formater
            precision (int): Nombre de décimales

        Returns:
            str: Pourcentage formaté
        """
        return f"{value:.{precision}f}%"

    @staticmethod
    def get_status_emoji(percentage: float, warning_threshold: float = 70.0, 
                         critical_threshold: float = 85.0) -> str:
        """Retourne l'emoji approprié selon le pourcentage d'utilisation.

        Args:
            percentage (float): Pourcentage d'utilisation
            warning_threshold (float): Seuil d'alerte warning
            critical_threshold (float): Seuil d'alerte critique

        Returns:
            str: Emoji correspondant au statut
        """
        if percentage < warning_threshold:
            return "🟢"
        elif percentage < critical_threshold:
            return "🟡"
        else:
            return "🔴"

    @staticmethod
    def calculate_uptime_string(start_time: datetime, current_time: datetime) -> str:
        """Calcule et formate le temps de fonctionnement.

        Args:
            start_time (datetime): Heure de démarrage
            current_time (datetime): Heure actuelle

        Returns:
            str: Durée formatée
        """
        uptime = current_time - start_time
        return str(uptime).split('.')[0]  # Supprime les microsecondes

    @staticmethod
    def sanitize_component_name(component: str) -> str:
        """Nettoie et valide un nom de composant.

        Args:
            component (str): Nom du composant à nettoyer

        Returns:
            str: Nom de composant nettoyé
        """
        return component.lower().strip().replace(" ", "_")

    @staticmethod
    def validate_percentage(value: float) -> bool:
        """Valide qu'une valeur est un pourcentage valide.

        Args:
            value (float): Valeur à valider

        Returns:
            bool: True si valide
        """
        return 0.0 <= value <= 100.0

    @staticmethod
    def merge_system_data(base_data: Dict[str, Any], 
                         additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fusionne deux dictionnaires de données système.

        Args:
            base_data (Dict[str, Any]): Données de base
            additional_data (Dict[str, Any]): Données supplémentaires

        Returns:
            Dict[str, Any]: Données fusionnées
        """
        merged = base_data.copy()
        merged.update(additional_data)
        return merged
