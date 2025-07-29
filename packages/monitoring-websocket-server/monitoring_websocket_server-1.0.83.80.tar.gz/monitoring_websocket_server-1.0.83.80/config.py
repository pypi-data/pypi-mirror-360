"""Configuration centralisée pour le système de monitoring.

Ce module contient toutes les constantes de configuration utilisées
dans l'ensemble du projet. Les constantes sont organisées par catégorie
pour faciliter la maintenance et la compréhension.

Les valeurs par défaut ont été choisies pour offrir un bon équilibre
entre performance et utilisation des ressources.
"""

# =============================================================================
# CONFIGURATION RÉSEAU WEBSOCKET
# =============================================================================
# Configuration du serveur WebSocket pour la diffusion des données de monitoring

#: Adresse IP d'écoute du serveur WebSocket
#: "0.0.0.0" permet d'écouter sur toutes les interfaces réseau
WEBSOCKET_HOST = "0.0.0.0"

#: Port d'écoute du serveur WebSocket
WEBSOCKET_PORT = 8765

#: Nombre maximum de clients WebSocket simultanés
WEBSOCKET_MAX_CLIENTS = 1000

#: Code de fermeture WebSocket quand la capacité maximale est atteinte
WEBSOCKET_CLOSE_CODE_CAPACITY = 1008

#: Timeout en secondes pour l'envoi de messages WebSocket
WEBSOCKET_SEND_TIMEOUT = 1.0

#: Limite du nombre d'envois WebSocket concurrents
#: Utilise un semaphore pour éviter la surcharge
WEBSOCKET_BROADCAST_SEMAPHORE_LIMIT = 50


# =============================================================================
# INTERVALLES DE TEMPS
# =============================================================================
# Définition des intervalles pour les différentes opérations du système

#: Intervalle en secondes entre chaque collecte de métriques
MONITOR_INTERVAL = 0.5

#: Intervalle en secondes entre chaque export de données
EXPORT_INTERVAL = 60.0

#: Intervalle en secondes pour la vérification du processeur
PROCESSOR_CHECK_INTERVAL = 0.05

#: Intervalle de fallback en secondes pour les mesures CPU
#: Utilisé quand l'intervalle normal échoue
PROCESSOR_FALLBACK_INTERVAL = 0.01

#: Intervalle en secondes pour le nettoyage périodique
CLEANUP_INTERVAL = 60.0

#: Durée de vie en secondes de l'historique des snapshots (1 heure)
HISTORY_TTL = 3600.0

#: Délai en secondes entre deux alertes identiques (5 minutes)
ALERT_COOLDOWN = 300.0

#: Intervalle en secondes pour le nettoyage des alertes (1 heure)
ALERT_CLEANUP_INTERVAL = 3600.0


# =============================================================================
# TAILLES DES FILES ET HISTORIQUES
# =============================================================================
# Limites de taille pour les différentes structures de données

#: Nombre maximum de snapshots conservés en mémoire
MAX_SNAPSHOTS_HISTORY = 1000

#: Taille maximale de l'historique des alertes
ALERT_HISTORY_SIZE = 100

#: Taille de la queue de données pour le service thread-safe
DATA_QUEUE_SIZE = 100

#: Taille de la queue des commandes
COMMAND_QUEUE_SIZE = 100

#: Taille de la queue des réponses
RESPONSE_QUEUE_SIZE = 100

#: Taille de la deque des dernières alertes
LAST_ALERTS_DEQUE_SIZE = 100


# =============================================================================
# LIMITES DE PERFORMANCE
# =============================================================================
# Limites pour éviter la surcharge du système

#: Nombre de workers dans le pool de threads
THREAD_POOL_WORKERS = 4

#: Nombre maximum d'erreurs avant overflow (1 million)
MAX_ERROR_COUNT = 1000000

#: Nombre maximum d'alertes avant overflow (10 millions)
MAX_ALERTS_COUNT = 10000000

#: Intervalle maximum en secondes pour la mesure du processeur
MAX_PROCESSOR_INTERVAL = 10.0

#: Intervalle maximum en secondes pour le monitoring (1 heure)
MAX_MONITORING_INTERVAL = 3600.0


# =============================================================================
# SEUILS D'ALERTES
# =============================================================================
# Valeurs de déclenchement pour les alertes système

# -----------------------------------------------------------------------------
# Seuils pour la mémoire RAM
# -----------------------------------------------------------------------------

#: Seuil d'avertissement pour l'utilisation mémoire (%)
MEMORY_WARNING_THRESHOLD = 80.0

#: Seuil critique pour l'utilisation mémoire (%)
MEMORY_CRITICAL_THRESHOLD = 90.0

# -----------------------------------------------------------------------------
# Seuils pour l'espace disque
# -----------------------------------------------------------------------------

#: Seuil d'avertissement pour l'utilisation disque (%)
DISK_WARNING_THRESHOLD = 85.0

#: Seuil critique pour l'utilisation disque (%)
DISK_CRITICAL_THRESHOLD = 95.0

#: Espace libre minimum en GB
DISK_MIN_FREE_GB = 1.0

#: Espace libre pour déclencher un avertissement (GB)
DISK_WARNING_FREE_GB = 2.0

#: Espace libre pour déclencher une alerte critique (GB)
DISK_CRITICAL_FREE_GB = 0.5



# =============================================================================
# TIMEOUTS
# =============================================================================
# Valeurs de timeout pour les différentes opérations

#: Timeout en secondes pour le démarrage du service
SERVICE_START_TIMEOUT = 10.0

#: Timeout en secondes pour l'arrêt du service
SERVICE_STOP_TIMEOUT = 5.0

#: Timeout en secondes pour l'ajout de commandes dans la queue
COMMAND_PUT_TIMEOUT = 1.0

#: Timeout en secondes pour la récupération de réponses
RESPONSE_GET_TIMEOUT = 2.0

#: Timeout en secondes pour les réponses d'export
EXPORT_RESPONSE_TIMEOUT = 5.0

#: Timeout en secondes pour le broadcast WebSocket
BROADCAST_TIMEOUT = 1.0

#: Temps d'attente en secondes pour que le serveur WebSocket soit prêt
WEBSOCKET_SERVER_READY_WAIT = 1.0

#: Timeout en secondes pour joindre un thread
THREAD_JOIN_TIMEOUT = 5.0


# =============================================================================
# CHEMINS ET FICHIERS
# =============================================================================
# Configuration des chemins par défaut

#: Répertoire par défaut pour l'export des données
DEFAULT_EXPORT_DIR = "./monitoring_data"

#: Chemin par défaut pour le monitoring disque
DEFAULT_DISK_PATH = "/"


# =============================================================================
# CONFIGURATION EXPORT
# =============================================================================
# Options par défaut pour l'export de données

#: Active la compression des fichiers exportés
EXPORT_COMPRESS_DEFAULT = False

#: Active le formatage indenté des fichiers JSON
EXPORT_PRETTY_PRINT_DEFAULT = True

#: Inclut la date dans le nom des fichiers exportés
EXPORT_DATE_IN_FILENAME_DEFAULT = True


# =============================================================================
# DÉLAIS ET RETRY
# =============================================================================
# Configuration des délais de retry et boucles

#: Délai en secondes avant de réessayer après une erreur
ERROR_RETRY_DELAY = 1.0

#: Délai en secondes de la boucle principale
MAIN_LOOP_DELAY = 0.1

#: Délai en secondes de la boucle d'erreur
ERROR_LOOP_DELAY = 0.5

#: Intervalle en secondes pour la collecte dans le serveur principal
MONITORING_COLLECTION_INTERVAL = 0.5


# =============================================================================
# SEUILS DE CHANGEMENT SIGNIFICATIF
# =============================================================================
# Seuils pour détecter les changements significatifs

#: Seuil de changement significatif pour l'utilisation CPU (%)
CPU_USAGE_CHANGE_THRESHOLD = 5.0

#: Seuil de changement significatif pour l'utilisation mémoire (%)
MEMORY_USAGE_CHANGE_THRESHOLD = 2.0

#: Seuil de changement significatif pour l'utilisation disque (%)
DISK_USAGE_CHANGE_THRESHOLD = 1.0


# =============================================================================
# AUTRES CONSTANTES
# =============================================================================
# Constantes diverses utilisées dans le système

#: Âge en secondes pour considérer une alerte comme ancienne (24 heures)
OLD_ALERT_AGE = 86400

#: Intervalle en secondes pour psutil.cpu_percent
CPU_PERCENT_INTERVAL = 0.1

#: Nombre de décimales pour l'affichage des valeurs
SIGNIFICANT_DIGITS = 2

#: Taille maximale par défaut des fichiers de log avant rotation (10 MB)
MAX_FILE_SIZE_DEFAULT = 10 * 1024 * 1024

#: Port SMTP par défaut pour l'envoi d'emails
SMTP_PORT_DEFAULT = 587

#: Timeout par défaut en secondes pour les requêtes HTTP
HTTP_TIMEOUT_DEFAULT = 10

#: Nombre maximum d'erreurs de monitoring avant réinitialisation
MAX_MONITOR_ERRORS = 10

#: Facteur de compression estimé pour gzip (30% de la taille originale)
COMPRESSION_FACTOR = 0.3

#: Niveau d'indentation pour le pretty print JSON
JSON_INDENT = 2


# =============================================================================
# CONFIGURATION LOGGING
# =============================================================================
# Configuration par défaut du système de logging

#: Niveau de log par défaut
DEFAULT_LOG_LEVEL = "INFO"

#: Format par défaut des messages de log
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"