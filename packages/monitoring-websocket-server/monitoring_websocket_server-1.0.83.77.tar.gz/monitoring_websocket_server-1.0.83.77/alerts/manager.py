"""
Gestionnaire d'alertes pour le système de monitoring.
Gestion des seuils, génération et historique des alertes.
"""

import time
import weakref
from collections import deque
from datetime import datetime
from typing import Dict, List, Deque, Optional, Callable, Any

from ..config import (
    ALERT_HISTORY_SIZE, ALERT_COOLDOWN, ALERT_CLEANUP_INTERVAL,
    MEMORY_WARNING_THRESHOLD, MEMORY_CRITICAL_THRESHOLD,
    DISK_WARNING_THRESHOLD, DISK_CRITICAL_THRESHOLD,
    OLD_ALERT_AGE
)
from ..core.models import Alert, MonitoringSnapshot
from ..core.enums import AlertLevel
from ..core.exceptions import AlertConfigurationError, InvalidThresholdError


class AlertManager:
    """Gestionnaire des alertes système."""

    def __init__(self, max_history: int = ALERT_HISTORY_SIZE, cooldown_seconds: float = ALERT_COOLDOWN) -> None:
        """Initialise le gestionnaire d'alertes.

        Args:
            max_history: Taille maximale de l'historique.
            cooldown_seconds: Délai entre alertes similaires en secondes.
        """
        self._thresholds: Dict[str, float] = self._initialize_default_thresholds()
        self._alerts_history: Deque[Alert] = deque(maxlen=max_history)
        self._last_alert_times: Dict[str, float] = {}
        self._cooldown_seconds: float = cooldown_seconds
        # Utiliser WeakSet pour les callbacks afin d'éviter les références circulaires
        self._alert_callbacks: weakref.WeakSet = weakref.WeakSet()
        self._enabled: bool = True
        self._last_cleanup_time: float = time.time()
        self._cleanup_interval: float = ALERT_CLEANUP_INTERVAL  # Cleanup interval

    @property
    def thresholds(self) -> Dict[str, float]:
        """Retourne les seuils d'alerte.

        Returns:
            Dictionnaire des seuils d'alerte.
        """
        return self._thresholds.copy()

    @property
    def alerts_history(self) -> List[Alert]:
        """Retourne l'historique des alertes.

        Returns:
            Liste des alertes générées.
        """
        return list(self._alerts_history)

    @property
    def cooldown_seconds(self) -> float:
        """Retourne le délai de cooldown.

        Returns:
            Délai en secondes entre alertes similaires.
        """
        return self._cooldown_seconds

    @cooldown_seconds.setter
    def cooldown_seconds(self, value: float) -> None:
        """Définit le délai de cooldown.

        Args:
            value: Nouveau délai en secondes.

        Raises:
            ValueError: Si le délai est négatif.
        """
        if value < 0:
            raise ValueError("Le délai de cooldown doit être positif")
        self._cooldown_seconds = value

    @property
    def enabled(self) -> bool:
        """Indique si le gestionnaire d'alertes est activé.

        Returns:
            True si le gestionnaire est activé, False sinon.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Active ou désactive le gestionnaire d'alertes.

        Args:
            value: Nouvel état du gestionnaire.
        """
        self._enabled = value

    @staticmethod
    def _initialize_default_thresholds() -> Dict[str, float]:
        """Initialise les seuils par défaut.

        Returns:
            Dictionnaire contenant les seuils par défaut pour chaque composant.
        """
        return {
            "memory_warning": MEMORY_WARNING_THRESHOLD,
            "memory_critical": MEMORY_CRITICAL_THRESHOLD,
            "disk_warning": DISK_WARNING_THRESHOLD,
            "disk_critical": DISK_CRITICAL_THRESHOLD
        }

    def set_threshold(self, component: str, level: str, value: float) -> None:
        """Définit un seuil d'alerte.

        Args:
            component: Composant (memory, disk).
            level: Niveau (warning, critical).
            value: Valeur du seuil en pourcentage.

        Raises:
            InvalidThresholdError: Si le seuil est invalide.
            AlertConfigurationError: Si la configuration est incorrecte.
        """
        # Validation du composant
        valid_components = ["memory", "disk"]
        if component not in valid_components:
            raise AlertConfigurationError(f"Composant invalide: {component}. Valides: {valid_components}")

        # Validation du niveau
        valid_levels = ["warning", "critical"]
        if level not in valid_levels:
            raise AlertConfigurationError(f"Niveau invalide: {level}. Valides: {valid_levels}")

        # Validation de la valeur
        if not 0.0 <= value <= 100.0:
            raise InvalidThresholdError(f"Le seuil doit être entre 0 et 100, reçu: {value}")

        key = f"{component}_{level}"
        
        # Vérification de cohérence (warning < critical)
        if level == "warning":
            critical_key = f"{component}_critical"
            if critical_key in self._thresholds and value >= self._thresholds[critical_key]:
                raise InvalidThresholdError(f"Le seuil warning ({value}) doit être inférieur au critical ({self._thresholds[critical_key]})")
        
        elif level == "critical":
            warning_key = f"{component}_warning"
            if warning_key in self._thresholds and value <= self._thresholds[warning_key]:
                raise InvalidThresholdError(f"Le seuil critical ({value}) doit être supérieur au warning ({self._thresholds[warning_key]})")

        self._thresholds[key] = value

    def get_threshold(self, component: str, level: str) -> Optional[float]:
        """Récupère un seuil spécifique.

        Args:
            component: Nom du composant.
            level: Niveau d'alerte.

        Returns:
            Valeur du seuil ou None si non défini.
        """
        key = f"{component}_{level}"
        return self._thresholds.get(key)

    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Ajoute un callback pour les nouvelles alertes.

        Args:
            callback: Fonction de callback à appeler lors d'une nouvelle alerte.
        """
        # WeakSet gère automatiquement la suppression des références mortes
        self._alert_callbacks.add(callback)

    def remove_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Supprime un callback.

        Args:
            callback: Fonction de callback à supprimer.
        """
        self._alert_callbacks.discard(callback)

    def clear_callbacks(self) -> None:
        """Supprime tous les callbacks."""
        self._alert_callbacks.clear()

    def check_thresholds(self, snapshot: MonitoringSnapshot) -> List[Alert]:
        """Vérifie les seuils et génère les alertes.

        Args:
            snapshot: Données de monitoring à vérifier.

        Returns:
            Liste des nouvelles alertes générées.
        """
        if not self._enabled:
            return []

        alerts = []
        current_time = time.time()

        # Vérification mémoire
        mem_percent = snapshot.memory_info.percentage
        alerts.extend(self._check_component_thresholds(
            "memory", mem_percent, current_time, snapshot.timestamp
        ))


        # Vérification disque
        disk_percent = snapshot.disk_info.percentage
        alerts.extend(self._check_component_thresholds(
            "disk", disk_percent, current_time, snapshot.timestamp
        ))

        # Ajout à l'historique et notification
        for alert in alerts:
            self._alerts_history.append(alert)
            self._notify_callbacks(alert)

        return alerts

    def _check_component_thresholds(self, component: str, value: float,
                                  current_time: float, timestamp: datetime) -> List[Alert]:
        """Vérifie les seuils pour un composant spécifique.

        Args:
            component: Nom du composant.
            value: Valeur actuelle en pourcentage.
            current_time: Timestamp actuel en secondes.
            timestamp: Timestamp de l'instantané.

        Returns:
            Liste des alertes générées pour ce composant.
        """
        alerts = []

        # Vérification critique en priorité
        critical_key = f"{component}_critical"
        critical_threshold = self._thresholds.get(critical_key, DISK_CRITICAL_THRESHOLD)

        if value > critical_threshold:
            if self._should_generate_alert(critical_key, current_time):
                alert = Alert(
                    timestamp=timestamp,
                    component=component,
                    metric="percentage",
                    value=value,
                    threshold=critical_threshold,
                    level=AlertLevel.CRITICAL,
                    message=f"CRITIQUE: {component.upper()} à {value:.1f}% (seuil: {critical_threshold}%)"
                )
                alerts.append(alert)
                self._last_alert_times[critical_key] = current_time

        # Vérification warning (seulement si pas critique)
        elif value > self._thresholds.get(f"{component}_warning", DISK_WARNING_THRESHOLD):
            warning_key = f"{component}_warning"
            warning_threshold = self._thresholds[warning_key]

            if self._should_generate_alert(warning_key, current_time):
                alert = Alert(
                    timestamp=timestamp,
                    component=component,
                    metric="percentage",
                    value=value,
                    threshold=warning_threshold,
                    level=AlertLevel.WARNING,
                    message=f"ATTENTION: {component.upper()} à {value:.1f}% (seuil: {warning_threshold}%)"
                )
                alerts.append(alert)
                self._last_alert_times[warning_key] = current_time

        return alerts

    def _should_generate_alert(self, alert_key: str, current_time: float) -> bool:
        """Vérifie si une alerte doit être générée (cooldown).

        Args:
            alert_key: Clé unique de l'alerte.
            current_time: Timestamp actuel en secondes.

        Returns:
            True si l'alerte doit être générée, False sinon.
        """
        # Nettoyer périodiquement au lieu de systématiquement
        if current_time - self._last_cleanup_time > self._cleanup_interval:
            self._cleanup_old_alert_times(current_time)
            self._last_cleanup_time = current_time
        
        last_time = self._last_alert_times.get(alert_key, 0)
        return (current_time - last_time) > self._cooldown_seconds
    
    def _cleanup_old_alert_times(self, current_time: float) -> None:
        """Nettoie les anciennes entrées du dictionnaire des alertes.
        
        Args:
            current_time: Timestamp actuel en secondes.
        """
        old_time = current_time - OLD_ALERT_AGE  # 24 heures
        # Créer un nouveau dictionnaire au lieu de modifier l'existant
        new_dict = {k: v for k, v in self._last_alert_times.items() if v > old_time}
        
        self._last_alert_times = new_dict

    def _notify_callbacks(self, alert: Alert) -> None:
        """Notifie tous les callbacks d'une nouvelle alerte.

        Args:
            alert: Alerte à notifier aux callbacks.
        """
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                # Log de l'erreur mais ne pas interrompre le processus
                print(f"Erreur dans callback d'alerte: {e}")

    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Récupère les alertes par niveau.

        Args:
            level: Niveau d'alerte à filtrer.

        Returns:
            Liste des alertes du niveau spécifié.
        """
        return [alert for alert in self._alerts_history if alert.level == level]

    def get_alerts_by_component(self, component: str) -> List[Alert]:
        """Récupère les alertes par composant.

        Args:
            component: Nom du composant à filtrer.

        Returns:
            Liste des alertes du composant spécifié.
        """
        return [alert for alert in self._alerts_history if alert.component == component]

    def get_recent_alerts(self, count: int = 10) -> List[Alert]:
        """Récupère les alertes les plus récentes.

        Args:
            count: Nombre d'alertes à retourner.

        Returns:
            Liste des alertes les plus récentes.
        """
        return list(self._alerts_history)[-count:] if self._alerts_history else []

    def clear_history(self) -> None:
        """Vide l'historique des alertes."""
        self._alerts_history.clear()
        self._last_alert_times.clear()

    def get_statistics(self) -> Dict[str, int]:
        """Retourne les statistiques des alertes.

        Returns:
            Dictionnaire contenant les statistiques par niveau et composant.
        """
        stats = {
            "total": len(self._alerts_history),
            "critical": len(self.get_alerts_by_level(AlertLevel.CRITICAL)),
            "warning": len(self.get_alerts_by_level(AlertLevel.WARNING)),
            "memory": len(self.get_alerts_by_component("memory")),
            "disk": len(self.get_alerts_by_component("disk"))
        }
        return stats

    def export_configuration(self) -> Dict[str, Any]:
        """Exporte la configuration actuelle.

        Returns:
            Dictionnaire contenant la configuration complète du gestionnaire.
        """
        return {
            "thresholds": self._thresholds.copy(),
            "cooldown_seconds": self._cooldown_seconds,
            "enabled": self._enabled,
            "max_history": self._alerts_history.maxlen
        }

    def import_configuration(self, config: Dict[str, Any]) -> None:
        """Importe une configuration.

        Args:
            config: Configuration à importer.

        Raises:
            AlertConfigurationError: Si la configuration est invalide.
        """
        try:
            if "thresholds" in config:
                # Validation et application des seuils
                for key, value in config["thresholds"].items():
                    if "_" in key:
                        component, level = key.split("_", 1)
                        self.set_threshold(component, level, value)
            
            if "cooldown_seconds" in config:
                self.cooldown_seconds = config["cooldown_seconds"]
            
            if "enabled" in config:
                self.enabled = config["enabled"]
                
        except Exception as e:
            raise AlertConfigurationError(f"Erreur lors de l'import de configuration: {e}")
