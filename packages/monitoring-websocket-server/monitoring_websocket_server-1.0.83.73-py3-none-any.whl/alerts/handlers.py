"""Handlers d'alertes pour le système de monitoring.

Ce module fournit différents types de gestionnaires pour traiter et distribuer
les alertes générées par le système de monitoring. Inclut des handlers pour
la console, les fichiers, les emails, les webhooks et Slack.

Classes:
    BaseAlertHandler: Classe de base abstraite pour tous les handlers.
    ConsoleAlertHandler: Handler pour affichage console.
    FileAlertHandler: Handler pour sauvegarde dans des fichiers.
    EmailAlertHandler: Handler pour envoi par email.
    WebhookAlertHandler: Handler pour envoi vers des webhooks HTTP.
    SlackAlertHandler: Handler spécialisé pour Slack.
    AlertHandlerManager: Gestionnaire centralisé des handlers.
"""

import smtplib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from urllib.request import urlopen, Request

from ..core.models import Alert
from ..core.enums import AlertLevel
from ..core.exceptions import AlertConfigurationError


class BaseAlertHandler(ABC):
    """Classe de base pour tous les handlers d'alertes.
    
    Définit l'interface commune que tous les handlers doivent implémenter
    et fournit des fonctionnalités de base pour le filtrage des alertes.
    
    Attributes:
        _name: Nom du handler.
        _enabled: État d'activation du handler.
        _handled_count: Nombre d'alertes traitées avec succès.
        _error_count: Nombre d'erreurs rencontrées.
    """

    def __init__(self, name: str, enabled: bool = True) -> None:
        """Initialise le handler de base.

        Args:
            name: Nom du handler.
            enabled: Indique si le handler est activé (défaut: True).
        """
        self._name: str = name
        self._enabled: bool = enabled
        self._filters: List[Callable[[Alert], bool]] = []
        self._handled_count: int = 0
        self._error_count: int = 0
        self._logger = logging.getLogger(f"{__name__}.{name}")

    @property
    def name(self) -> str:
        """Retourne le nom du handler.

        Returns:
            Nom du handler.
        """
        return self._name

    @property
    def enabled(self) -> bool:
        """Indique si le handler est activé.

        Returns:
            True si le handler est activé, False sinon.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Active ou désactive le handler.

        Args:
            value: Nouvel état d'activation.
        """
        self._enabled = value

    @property
    def handled_count(self) -> int:
        """Retourne le nombre d'alertes traitées.

        Returns:
            Nombre d'alertes traitées avec succès.
        """
        return self._handled_count

    @property
    def error_count(self) -> int:
        """Retourne le nombre d'erreurs rencontrées.

        Returns:
            Nombre d'erreurs lors du traitement des alertes.
        """
        return self._error_count

    def add_filter(self, filter_func: Callable[[Alert], bool]) -> None:
        """Ajoute un filtre pour les alertes.

        Args:
            filter_func: Fonction de filtrage qui prend une alerte et
                retourne True si l'alerte doit être traitée.
        """
        self._filters.append(filter_func)

    def remove_filter(self, filter_func: Callable[[Alert], bool]) -> None:
        """Supprime un filtre.

        Args:
            filter_func: Fonction de filtrage à supprimer.
        """
        if filter_func in self._filters:
            self._filters.remove(filter_func)

    def clear_filters(self) -> None:
        """Supprime tous les filtres."""
        self._filters.clear()

    def should_handle(self, alert: Alert) -> bool:
        """Vérifie si l'alerte doit être traitée par ce handler.

        Args:
            alert: Alerte à vérifier.

        Returns:
            True si l'alerte passe tous les filtres et doit être traitée.
        """
        if not self._enabled:
            return False

        # Application des filtres
        for filter_func in self._filters:
            try:
                if not filter_func(alert):
                    return False
            except Exception as e:
                self._logger.error(f"Erreur dans le filtre {filter_func}: {e}")
                return False

        return True

    def handle(self, alert: Alert) -> bool:
        """Traite une alerte si elle passe les filtres.

        Args:
            alert: Alerte à traiter.

        Returns:
            True si l'alerte a été traitée avec succès, False en cas d'erreur.
        """
        if not self.should_handle(alert):
            return True  # Pas d'erreur, juste ignoré

        try:
            success = self._handle_alert(alert)
            if success:
                # Limite handled_count avec modulo pour éviter overflow
                self._handled_count = (self._handled_count + 1) % 10000000
            else:
                # Limite error_count avec modulo pour éviter overflow
                self._error_count = (self._error_count + 1) % 1000000
            return success
        except Exception as e:
            self._logger.error(f"Erreur lors du traitement de l'alerte: {e}")
            # Limite error_count avec modulo pour éviter overflow
            self._error_count = (self._error_count + 1) % 1000000
            return False

    @abstractmethod
    def _handle_alert(self, alert: Alert) -> bool:
        """Méthode de traitement spécifique à implémenter.

        Args:
            alert: Alerte à traiter.

        Returns:
            True si traité avec succès, False sinon.
        """
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du handler.

        Returns:
            Dictionnaire contenant les statistiques du handler (nom, état,
            nombre d'alertes traitées, nombre d'erreurs, nombre de filtres).
        """
        return {
            "name": self._name,
            "enabled": self._enabled,
            "handled_count": self._handled_count,
            "error_count": self._error_count,
            "filters_count": len(self._filters)
        }

    def __str__(self) -> str:
        """Retourne une représentation textuelle du handler.
        
        Returns:
            Représentation du handler au format
            "ClasseName(name='nom', enabled=état)".
        """
        return f"{self.__class__.__name__}(name='{self._name}', enabled={self._enabled})"


class ConsoleAlertHandler(BaseAlertHandler):
    """Handler qui affiche les alertes dans la console.
    
    Ce handler affiche les alertes formatées dans la console avec support
    optionnel des couleurs ANSI et des emojis selon le niveau d'alerte.
    """

    def __init__(self, name: str = "console", colored: bool = True, 
                 timestamp_format: str = "%Y-%m-%d %H:%M:%S") -> None:
        """Initialise le handler console.

        Args:
            name: Nom du handler (défaut: "console").
            colored: Utiliser des couleurs ANSI (défaut: True).
            timestamp_format: Format d'affichage des timestamps
                (défaut: "%Y-%m-%d %H:%M:%S").
        """
        super().__init__(name)
        self._colored: bool = colored
        self._timestamp_format: str = timestamp_format

    @property
    def colored(self) -> bool:
        """Indique si les couleurs sont activées.

        Returns:
            True si les couleurs ANSI sont activées.
        """
        return self._colored

    @colored.setter
    def colored(self, value: bool) -> None:
        """Active ou désactive les couleurs.

        Args:
            value: Nouvel état d'activation des couleurs.
        """
        self._colored = value

    def _handle_alert(self, alert: Alert) -> bool:
        """Affiche l'alerte dans la console.

        Args:
            alert: Alerte à afficher.

        Returns:
            Toujours True (affichage ne peut pas échouer).
        """
        timestamp = alert.timestamp.strftime(self._timestamp_format)
        
        if self._colored:
            # Couleurs ANSI selon le niveau
            color_codes = {
                AlertLevel.INFO: "\033[94m",      # Bleu
                AlertLevel.WARNING: "\033[93m",   # Jaune
                AlertLevel.CRITICAL: "\033[91m"   # Rouge
            }
            reset_code = "\033[0m"
            
            color = color_codes.get(alert.level, "")
            level_text = f"{color}{alert.level.value.upper()}{reset_code}"
        else:
            level_text = alert.level.value.upper()

        # Emoji selon le niveau
        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🔴"
        }
        emoji = emoji_map.get(alert.level, "")

        print(f"{emoji} [{timestamp}] {level_text} - {alert.component.upper()}: {alert.message}")
        return True


class FileAlertHandler(BaseAlertHandler):
    """Handler qui sauvegarde les alertes dans un fichier.
    
    Ce handler écrit les alertes dans un fichier avec rotation automatique
    selon la taille. Supporte les formats texte et JSON.
    """

    def __init__(self, name: str = "file", log_file: str = "./alerts.log",
                 format_json: bool = False, max_file_size: int = 10 * 1024 * 1024) -> None:
        """Initialise le handler fichier.

        Args:
            name: Nom du handler (défaut: "file").
            log_file: Chemin du fichier de log (défaut: "./alerts.log").
            format_json: Sauvegarder au format JSON (défaut: False).
            max_file_size: Taille maximale du fichier en bytes avant rotation
                (défaut: 10MB).
        """
        super().__init__(name)
        self._log_file: Path = Path(log_file)
        self._format_json: bool = format_json
        self._max_file_size: int = max_file_size
        
        # Création du répertoire parent si nécessaire
        self._log_file.parent.mkdir(parents=True, exist_ok=True)

    @property
    def log_file(self) -> Path:
        """Retourne le chemin du fichier de log.

        Returns:
            Chemin du fichier de log.
        """
        return self._log_file

    def _handle_alert(self, alert: Alert) -> bool:
        """Sauvegarde l'alerte dans le fichier.

        Args:
            alert: Alerte à sauvegarder.

        Returns:
            True si sauvegardé avec succès, False en cas d'erreur.
        """
        try:
            # Rotation du fichier si nécessaire
            self._rotate_if_needed()
            
            if self._format_json:
                alert_data = {
                    "timestamp": alert.timestamp.isoformat(),
                    "level": alert.level.value,
                    "component": alert.component,
                    "metric": alert.metric,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "message": alert.message
                }
                line = json.dumps(alert_data, ensure_ascii=False) + "\n"
            else:
                timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                line = f"[{timestamp}] {alert.level.value.upper()} - {alert.component.upper()}: {alert.message}\n"
            
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(line)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur lors de l'écriture dans {self._log_file}: {e}")
            return False

    def _rotate_if_needed(self) -> None:
        """Effectue une rotation du fichier si nécessaire.
        
        La rotation est déclenchée lorsque le fichier dépasse la taille maximale
        configurée. Le fichier actuel est renommé avec un timestamp.
        """
        if not self._log_file.exists():
            return
        
        if self._log_file.stat().st_size > self._max_file_size:
            backup_file = self._log_file.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            self._log_file.rename(backup_file)
            self._logger.info(f"Rotation du fichier de log vers {backup_file}")


class EmailAlertHandler(BaseAlertHandler):
    """Handler qui envoie les alertes par email.
    
    Ce handler utilise SMTP pour envoyer des alertes par email avec support
    optionnel de l'authentification et du TLS.
    """

    def __init__(self, name: str = "email", smtp_host: str = "localhost",
                 smtp_port: int = 587, username: Optional[str] = None,
                 password: Optional[str] = None, use_tls: bool = True,
                 from_email: str = "monitoring@example.com",
                 to_emails: List[str] = None) -> None:
        """Initialise le handler email.

        Args:
            name: Nom du handler (défaut: "email").
            smtp_host: Serveur SMTP (défaut: "localhost").
            smtp_port: Port SMTP (défaut: 587).
            username: Nom d'utilisateur SMTP (optionnel).
            password: Mot de passe SMTP (optionnel).
            use_tls: Utiliser TLS (défaut: True).
            from_email: Adresse d'expéditeur (défaut: "monitoring@example.com").
            to_emails: Liste des destinataires (défaut: liste vide).
        """
        super().__init__(name)
        self._smtp_host: str = smtp_host
        self._smtp_port: int = smtp_port
        self._username: Optional[str] = username
        self._password: Optional[str] = password
        self._use_tls: bool = use_tls
        self._from_email: str = from_email
        self._to_emails: List[str] = to_emails or []

    def add_recipient(self, email: str) -> None:
        """Ajoute un destinataire.

        Args:
            email: Adresse email à ajouter.
        """
        if email not in self._to_emails:
            self._to_emails.append(email)

    def remove_recipient(self, email: str) -> None:
        """Supprime un destinataire.

        Args:
            email: Adresse email à supprimer.
        """
        if email in self._to_emails:
            self._to_emails.remove(email)

    def _handle_alert(self, alert: Alert) -> bool:
        """Envoie l'alerte par email.

        Args:
            alert: Alerte à envoyer.

        Returns:
            True si envoyé avec succès, False en cas d'erreur.
        """
        if not self._to_emails:
            self._logger.warning("Aucun destinataire configuré pour les emails")
            return False

        try:
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = self._from_email
            msg['To'] = ", ".join(self._to_emails)
            msg['Subject'] = f"Alerte Monitoring - {alert.level.value.upper()} - {alert.component}"

            # Corps du message
            body = self._create_email_body(alert)
            msg.attach(MIMEText(body, 'html' if '<' in body else 'plain'))

            # Envoi
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                if self._use_tls:
                    server.starttls()
                if self._username and self._password:
                    server.login(self._username, self._password)
                server.send_message(msg)

            return True

        except Exception as e:
            self._logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return False

    @staticmethod
    def _create_email_body(alert: Alert) -> str:
        """Crée le corps de l'email pour l'alerte.

        Args:
            alert: Alerte à formater.

        Returns:
            Corps de l'email formaté en texte brut.
        """
        timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
            Alerte de Monitoring Système

            Niveau: {alert.level.value.upper()}
            Composant: {alert.component.upper()}
            Métrique: {alert.metric}
            Valeur actuelle: {alert.value:.2f}%
            Seuil configuré: {alert.threshold:.2f}%
            Timestamp: {timestamp}

            Message: {alert.message}

            ---
            Système de Monitoring Automatique
        """.strip()


class WebhookAlertHandler(BaseAlertHandler):
    """Handler qui envoie les alertes vers un webhook HTTP.
    
    Ce handler envoie les alertes au format JSON vers une URL HTTP/HTTPS
    configurée avec support des headers personnalisés.
    """

    def __init__(self, name: str = "webhook", webhook_url: str = "",
                 timeout: int = 10, headers: Optional[Dict[str, str]] = None) -> None:
        """Initialise le handler webhook.

        Args:
            name: Nom du handler (défaut: "webhook").
            webhook_url: URL du webhook (défaut: chaîne vide).
            timeout: Timeout en secondes (défaut: 10).
            headers: Headers HTTP personnalisés (optionnel).
        """
        super().__init__(name)
        self._webhook_url: str = webhook_url
        self._timeout: int = timeout
        self._headers: Dict[str, str] = headers or {}

    @property
    def webhook_url(self) -> str:
        """Retourne l'URL du webhook.

        Returns:
            URL du webhook.
        """
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, url: str) -> None:
        """Définit l'URL du webhook.

        Args:
            url: Nouvelle URL du webhook.
        """
        self._webhook_url = url

    def _handle_alert(self, alert: Alert) -> bool:
        """Envoie l'alerte vers le webhook.

        Args:
            alert: Alerte à envoyer.

        Returns:
            True si envoyé avec succès (status HTTP 2xx), False sinon.
        """
        if not self._webhook_url:
            self._logger.warning("Aucune URL de webhook configurée")
            return False

        try:
            # Préparation des données
            payload = {
                "timestamp": alert.timestamp.isoformat(),
                "level": alert.level.value,
                "component": alert.component,
                "metric": alert.metric,
                "value": alert.value,
                "threshold": alert.threshold,
                "message": alert.message
            }

            # Headers par défaut
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "MonitoringSystem/1.0"
            }
            headers.update(self._headers)

            # Préparation de la requête
            data = json.dumps(payload).encode('utf-8')
            request = Request(self._webhook_url, data=data, headers=headers)

            # Envoi
            with urlopen(request, timeout=self._timeout) as response:
                if 200 <= response.status < 300:
                    return True
                else:
                    self._logger.error(f"Webhook a retourné le status {response.status}")
                    return False

        except Exception as e:
            self._logger.error(f"Erreur lors de l'envoi vers le webhook: {e}")
            return False


class SlackAlertHandler(WebhookAlertHandler):
    """Handler spécialisé pour Slack utilisant les webhooks entrants.
    
    Ce handler formate les alertes selon l'API Slack avec attachments
    colorés et emojis selon le niveau d'alerte.
    """

    def __init__(self, name: str = "slack", webhook_url: str = "",
                 channel: Optional[str] = None, username: str = "MonitoringBot") -> None:
        """Initialise le handler Slack.

        Args:
            name: Nom du handler (défaut: "slack").
            webhook_url: URL du webhook Slack (défaut: chaîne vide).
            channel: Canal Slack (optionnel, utilise le canal par défaut du webhook).
            username: Nom d'utilisateur du bot (défaut: "MonitoringBot").
        """
        super().__init__(name, webhook_url)
        self._channel: Optional[str] = channel
        self._username: str = username

    def _handle_alert(self, alert: Alert) -> bool:
        """Envoie l'alerte vers Slack.

        Args:
            alert: Alerte à envoyer.

        Returns:
            True si envoyé avec succès, False sinon.
        """
        if not self._webhook_url:
            self._logger.warning("Aucune URL de webhook Slack configurée")
            return False

        try:
            # Couleurs selon le niveau
            color_map = {
                AlertLevel.INFO: "#36a64f",      # Vert
                AlertLevel.WARNING: "#ff9500",   # Orange
                AlertLevel.CRITICAL: "#ff0000"   # Rouge
            }

            # Emoji selon le niveau
            emoji_map = {
                AlertLevel.INFO: ":information_source:",
                AlertLevel.WARNING: ":warning:",
                AlertLevel.CRITICAL: ":red_circle:"
            }

            # Préparation du payload Slack
            payload = {
                "username": self._username,
                "attachments": [
                    {
                        "color": color_map.get(alert.level, "#000000"),
                        "title": f"{emoji_map.get(alert.level, '')} Alerte {alert.level.value.upper()}",
                        "fields": [
                            {
                                "title": "Composant",
                                "value": alert.component.upper(),
                                "short": True
                            },
                            {
                                "title": "Valeur",
                                "value": f"{alert.value:.1f}% (seuil: {alert.threshold:.1f}%)",
                                "short": True
                            },
                            {
                                "title": "Message",
                                "value": alert.message,
                                "short": False
                            }
                        ],
                        "footer": "Système de Monitoring",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }

            if self._channel:
                payload["channel"] = self._channel

            # Headers Slack
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "MonitoringSystem-Slack/1.0"
            }

            # Envoi
            data = json.dumps(payload).encode('utf-8')
            request = Request(self._webhook_url, data=data, headers=headers)

            with urlopen(request, timeout=self._timeout) as response:
                if response.status == 200:
                    return True
                else:
                    self._logger.error(f"Slack webhook a retourné le status {response.status}")
                    return False

        except Exception as e:
            self._logger.error(f"Erreur lors de l'envoi vers Slack: {e}")
            return False


class AlertHandlerManager:
    """Gestionnaire centralisé pour tous les handlers d'alertes.
    
    Cette classe coordonne la distribution des alertes vers plusieurs handlers
    et gère leur cycle de vie (ajout, suppression, activation/désactivation).
    """

    def __init__(self) -> None:
        """Initialise le gestionnaire de handlers."""
        self._handlers: Dict[str, BaseAlertHandler] = {}
        self._logger = logging.getLogger(f"{__name__}.Manager")

    def add_handler(self, handler: BaseAlertHandler) -> None:
        """Ajoute un handler.

        Args:
            handler: Handler à ajouter.

        Raises:
            AlertConfigurationError: Si un handler avec le même nom existe déjà.
        """
        if handler.name in self._handlers:
            raise AlertConfigurationError(f"Un handler nommé '{handler.name}' existe déjà")
        
        self._handlers[handler.name] = handler
        self._logger.info(f"Handler '{handler.name}' ajouté")

    def remove_handler(self, name: str) -> bool:
        """Supprime un handler.

        Args:
            name: Nom du handler à supprimer.

        Returns:
            True si le handler a été supprimé, False s'il n'existait pas.
        """
        if name in self._handlers:
            del self._handlers[name]
            self._logger.info(f"Handler '{name}' supprimé")
            return True
        return False

    def get_handler(self, name: str) -> Optional[BaseAlertHandler]:
        """Récupère un handler par son nom.

        Args:
            name: Nom du handler.

        Returns:
            Handler correspondant ou None s'il n'existe pas.
        """
        return self._handlers.get(name)

    def list_handlers(self) -> List[str]:
        """Retourne la liste des noms de handlers.

        Returns:
            Liste des noms de tous les handlers enregistrés.
        """
        return list(self._handlers.keys())

    def handle_alert(self, alert: Alert) -> Dict[str, bool]:
        """Distribue une alerte à tous les handlers activés.

        Args:
            alert: Alerte à distribuer.

        Returns:
            Dictionnaire avec le nom du handler comme clé et le résultat
            du traitement (True/False) comme valeur.
        """
        results = {}
        
        for name, handler in self._handlers.items():
            if handler.enabled:
                try:
                    results[name] = handler.handle(alert)
                except Exception as e:
                    self._logger.error(f"Erreur dans le handler '{name}': {e}")
                    results[name] = False
            else:
                results[name] = True  # Désactivé = pas d'erreur

        return results

    def get_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Retourne les statistiques de tous les handlers.

        Returns:
            Dictionnaire avec le nom du handler comme clé et ses statistiques
            comme valeur.
        """
        return {name: handler.get_statistics() for name, handler in self._handlers.items()}

    def enable_all(self) -> None:
        """Active tous les handlers."""
        for handler in self._handlers.values():
            handler.enabled = True

    def disable_all(self) -> None:
        """Désactive tous les handlers."""
        for handler in self._handlers.values():
            handler.enabled = False

    def clear_all(self) -> None:
        """Supprime tous les handlers."""
        self._handlers.clear()
        self._logger.info("Tous les handlers supprimés")


# ===================================================================
# FILTRES PRÉDÉFINIS
# ===================================================================

def create_level_filter(min_level: AlertLevel) -> Callable[[Alert], bool]:
    """Crée un filtre par niveau d'alerte.

    Args:
        min_level: Niveau minimum accepté (INFO, WARNING ou CRITICAL).

    Returns:
        Fonction de filtrage qui retourne True si l'alerte a un niveau
        supérieur ou égal au niveau minimum.
    """
    level_order = {
        AlertLevel.INFO: 0,
        AlertLevel.WARNING: 1,
        AlertLevel.CRITICAL: 2
    }
    
    min_order = level_order[min_level]
    
    def filter_func(alert: Alert) -> bool:
        return level_order.get(alert.level, 0) >= min_order
    
    return filter_func


def create_component_filter(components: List[str]) -> Callable[[Alert], bool]:
    """Crée un filtre par composant.

    Args:
        components: Liste des composants autorisés.

    Returns:
        Fonction de filtrage qui retourne True si l'alerte provient
        d'un des composants autorisés.
    """
    def filter_func(alert: Alert) -> bool:
        return alert.component in components
    
    return filter_func


def create_time_filter(start_hour: int = 0, end_hour: int = 23) -> Callable[[Alert], bool]:
    """Crée un filtre par heure de la journée.

    Args:
        start_hour: Heure de début (0-23, défaut: 0).
        end_hour: Heure de fin (0-23, défaut: 23).

    Returns:
        Fonction de filtrage qui retourne True si l'alerte est dans
        la plage horaire spécifiée. Supporte les plages qui traversent
        minuit (ex: 22h-2h).
    """
    def filter_func(alert: Alert) -> bool:
        current_hour = alert.timestamp.hour
        if start_hour <= end_hour:
            return start_hour <= current_hour <= end_hour
        else:  # Période qui traverse minuit
            return current_hour >= start_hour or current_hour <= end_hour
    
    return filter_func
