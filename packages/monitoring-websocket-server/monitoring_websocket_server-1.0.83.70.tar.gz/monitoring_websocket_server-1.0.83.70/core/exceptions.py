"""Exceptions personnalisées pour le système de monitoring.

Ce module définit la hiérarchie d'exceptions spécifiques au système
de monitoring, permettant une gestion d'erreurs granulaire et précise.

Classes:
    MonitoringError: Exception de base pour toutes les erreurs du système
    MonitorInitializationError: Erreur d'initialisation d'un moniteur
    DataCollectionError: Erreur de collecte de données
    ServiceStartupError: Erreur de démarrage du service
    ServiceShutdownError: Erreur d'arrêt du service
    AlertConfigurationError: Erreur de configuration des alertes
    ExportError: Erreur d'export de données
    InvalidThresholdError: Seuil d'alerte invalide
    InvalidIntervalError: Intervalle de monitoring invalide
"""


class MonitoringError(Exception):
    """Exception de base pour le système de monitoring.
    
    Toutes les exceptions spécifiques au monitoring doivent hériter
    de cette classe pour faciliter la gestion d'erreurs globale.
    """
    pass


class MonitorInitializationError(MonitoringError):
    """Erreur lors de l'initialisation d'un moniteur.
    
    Levée quand un moniteur ne peut pas être initialisé correctement,
    par exemple en cas d'absence de permissions ou de ressources.
    """
    pass


class DataCollectionError(MonitoringError):
    """Erreur lors de la collecte de données système.
    
    Levée quand un moniteur échoue à collecter les données requises
    après une initialisation réussie.
    """
    pass


class ServiceStartupError(MonitoringError):
    """Erreur lors du démarrage du service.
    
    Levée quand le service de monitoring ne peut pas démarrer
    correctement ses threads ou initialiser ses composants.
    """
    pass


class ServiceShutdownError(MonitoringError):
    """Erreur lors de l'arrêt du service.
    
    Levée quand le service ne peut pas s'arrêter proprement,
    par exemple en cas de threads bloqués ou de ressources non libérées.
    """
    pass


class AlertConfigurationError(MonitoringError):
    """Erreur de configuration des alertes.
    
    Levée quand la configuration des alertes est invalide,
    par exemple avec des seuils incohérents ou des handlers manquants.
    """
    pass


class ExportError(MonitoringError):
    """Erreur lors de l'export des données.
    
    Levée quand les données ne peuvent pas être exportées,
    par exemple en cas de problème d'accès fichier ou réseau.
    """
    pass


class InvalidThresholdError(AlertConfigurationError):
    """Seuil d'alerte invalide.
    
    Levée quand un seuil d'alerte est hors des limites acceptables
    (par exemple, pourcentage > 100 ou valeur négative).
    """
    pass


class InvalidIntervalError(MonitoringError):
    """Intervalle de monitoring invalide.
    
    Levée quand un intervalle de temps est invalide,
    par exemple une valeur négative ou zéro.
    """
    pass
