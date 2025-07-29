"""Module de gestion des alertes pour le système de monitoring.

Ce module fournit un système complet de gestion des alertes avec support
de multiples handlers (console, fichier, email) et gestion des seuils
configurables.

Classes exportées:
    AlertManager: Gestionnaire principal des alertes
    BaseAlertHandler: Classe de base pour les handlers d'alertes
    ConsoleAlertHandler: Handler pour affichage console
    FileAlertHandler: Handler pour enregistrement dans des fichiers
    EmailAlertHandler: Handler pour envoi d'emails
"""

from .manager import AlertManager
from .handlers import (
    BaseAlertHandler,
    ConsoleAlertHandler,
    FileAlertHandler,
    EmailAlertHandler
)

__all__ = [
    "AlertManager",
    "BaseAlertHandler",
    "ConsoleAlertHandler",
    "FileAlertHandler",
    "EmailAlertHandler"
]