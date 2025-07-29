# Système de Monitoring WebSocket en Temps Réel

Un système complet de surveillance des ressources système avec diffusion en temps réel via WebSocket. Collecte les métriques CPU, mémoire, disque et GPU, avec un système d'alertes configurable.

## Table des Matières

- [1. Installation](#1-installation)
- [2. Démarrage Rapide](#2-démarrage-rapide)
- [3. Fonctionnalités](#3-fonctionnalités)
- [4. Configuration](#4-configuration)
- [5. API WebSocket](#5-api-websocket)
- [6. Métriques Collectées](#6-métriques-collectées)
- [7. Système d'Alertes](#7-système-dalertes)
- [8. Utilisation Avancée](#8-utilisation-avancée)
- [9. Intégration](#9-intégration)
- [10. Architecture](#10-architecture)

## 1. Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- (Optionnel) Drivers NVIDIA pour le monitoring GPU

### Installation via pip

```bash
pip install monitoring-websocket-server
```

### Installation depuis les sources

```bash
# Cloner le repository
git clone https://github.com/votre-repo/monitoring-websocket-system-server.git
cd monitoring-websocket-system-server

# Installer les dépendances
pip install -r requirements.txt
```

### Dépendances

**Obligatoires :**
- `psutil` : Collecte des métriques système
- `websockets` : Serveur WebSocket
- `colorama` : Affichage coloré dans la console

**Optionnelles (pour le monitoring GPU) :**
- `GPUtil` : Interface simplifiée pour les GPU NVIDIA
- `nvidia-ml-py3` ou `pynvml` : Accès direct à l'API NVIDIA

## 2. Démarrage Rapide

### 1. Lancer le serveur de monitoring

```bash
# Serveur avec configuration par défaut
monitoring-websocket-server

# Serveur avec options CLI
monitoring-websocket-server --host 127.0.0.1 --port 8080
```

Le serveur démarre sur `ws://0.0.0.0:8765` par défaut. Ces valeurs peuvent être modifiées dans `config.py`.

### 2. Connexion au serveur

Une fois le serveur lancé, vous pouvez vous y connecter via WebSocket à l'adresse `ws://localhost:8765`.

Voir la section [API WebSocket](#5-api-websocket) pour des exemples de clients en JavaScript et Python.

## 3. Fonctionnalités

### Collecte de Métriques en Temps Réel

- **CPU/Processeur**
  - Utilisation globale et par cœur
  - Fréquence actuelle et maximale
  - Nombre de cœurs physiques et logiques
  
- **Mémoire RAM**
  - Utilisation totale, disponible et utilisée
  - Pourcentage d'utilisation
  
- **Disque**
  - Espace total, utilisé et libre
  - Pourcentage d'utilisation
  - Surveillance de chemins spécifiques
  
- **GPU** (si disponible)
  - Nom et version du driver
  - Support multi-GPU avec détection automatique
  - Backends multiples : GPUtil → pynvml → nvidia-smi (fallback)
  - Méthodes utilitaires : `get_gpu_count()`, `is_gpu_available()`
  - Utilisation GPU et mémoire
  - Température et consommation
  - Support multi-GPU

- **Informations Système**
  - OS, version, architecture
  - Hostname et nombre de processus
  - Heure de démarrage système

- **Alertes en Temps Réel**
  - Génération automatique lors du dépassement de seuils
  - Deux niveaux : WARNING et CRITICAL
  - Seuils par défaut :
    - Mémoire : WARNING à 80%, CRITICAL à 90%
    - Disque : WARNING à 85%, CRITICAL à 95%
  - Diffusion instantanée via WebSocket
  - Structure détaillée avec timestamp, composant, valeur et message

### Diffusion WebSocket

- Serveur WebSocket haute performance
- Support jusqu'à 1000 clients simultanés
- Messages JSON structurés avec horodatage
- Reconnexion automatique côté client
- Broadcast optimisé avec limitation de débit
- **Alertes intégrées dans les messages de monitoring**

### Système d'Alertes

- Alertes configurables sur seuils
- Niveaux WARNING et CRITICAL
- Cooldown pour éviter le spam
- Handlers multiples (console, fichier, email)
- Callbacks personnalisables

### Export de Données

- Export JSON avec rotation automatique
- Compression optionnelle
- Horodatage des fichiers
- Configuration flexible des répertoires

## 4. Configuration

### Système de Configuration

La configuration du système est centralisée dans le fichier `config.py` qui contient toutes les constantes utilisées dans le projet. Les valeurs sont organisées par catégorie pour faciliter la maintenance.

#### Modification de la Configuration

Pour modifier la configuration, éditez directement les constantes dans le fichier `config.py` :

```python
# Exemple de modification de config.py
from config import *

# Modifier l'intervalle de monitoring
MONITOR_INTERVAL = 1.0  # Passer de 0.5 à 1 seconde

# Modifier les seuils d'alerte mémoire
MEMORY_WARNING_THRESHOLD = 75.0  # Au lieu de 80%
MEMORY_CRITICAL_THRESHOLD = 85.0  # Au lieu de 90%
```

#### Catégories de Configuration

**Configuration Réseau WebSocket**
```python
WEBSOCKET_HOST = "0.0.0.0"          # Interface d'écoute
WEBSOCKET_PORT = 8765               # Port du serveur
WEBSOCKET_MAX_CLIENTS = 1000        # Clients max simultanés
WEBSOCKET_SEND_TIMEOUT = 1.0        # Timeout envoi (secondes)
```

**Intervalles de Temps**
```python
MONITOR_INTERVAL = 0.5              # Collecte métriques (secondes)
EXPORT_INTERVAL = 60.0              # Export JSON (secondes)
CLEANUP_INTERVAL = 60.0             # Nettoyage périodique (secondes)
ALERT_COOLDOWN = 300.0              # Entre alertes identiques (secondes)
```

**Seuils d'Alertes**
```python
# Mémoire RAM
MEMORY_WARNING_THRESHOLD = 80.0     # Seuil warning (%)
MEMORY_CRITICAL_THRESHOLD = 90.0    # Seuil critique (%)

# Disque
DISK_WARNING_THRESHOLD = 85.0       # Seuil warning (%)
DISK_CRITICAL_THRESHOLD = 95.0      # Seuil critique (%)
DISK_MIN_FREE_GB = 1.0             # Espace libre minimum (GB)

```

**Limites et Tailles**
```python
MAX_SNAPSHOTS_HISTORY = 1000        # Snapshots en mémoire
THREAD_POOL_WORKERS = 4             # Workers ThreadPool
DATA_QUEUE_SIZE = 100               # Taille queue thread-safe
WEBSOCKET_BROADCAST_SEMAPHORE_LIMIT = 50  # Envois concurrents
```

### Utilisation dans le Code

Les services et composants utilisent automatiquement ces constantes :

```python
from services.realtime import RealtimeMonitoringService

# Le service utilise les constantes de config.py par défaut
service = RealtimeMonitoringService()

# Ou surcharge avec des valeurs spécifiques
service = RealtimeMonitoringService(
    monitor_interval=1.0,  # Surcharge MONITOR_INTERVAL
    export_interval=30.0   # Surcharge EXPORT_INTERVAL
)
```

### Valeurs par Défaut Principales

| Catégorie | Constante | Valeur | Description |
|-----------|-----------|---------|-------------|
| **WebSocket** | `WEBSOCKET_PORT` | 8765 | Port du serveur |
| **Monitoring** | `MONITOR_INTERVAL` | 0.5s | Fréquence collecte |
| **Export** | `EXPORT_INTERVAL` | 60s | Fréquence export JSON |
| **Historique** | `MAX_SNAPSHOTS_HISTORY` | 1000 | Snapshots max |
| **Alertes** | `ALERT_COOLDOWN` | 300s | Délai entre alertes |
| **Mémoire** | `MEMORY_WARNING_THRESHOLD` | 80% | Seuil warning RAM |
| **Disque** | `DISK_WARNING_THRESHOLD` | 85% | Seuil warning disque |

### Documentation Complète

Le fichier `config.py` est entièrement documenté avec :
- Docstrings PEP 257 pour chaque constante
- Organisation par sections clairement identifiées
- Commentaires explicatifs pour les valeurs critiques
- Valeurs par défaut optimisées pour la performance

Consultez directement `config.py` pour voir toutes les options disponibles et leur documentation détaillée.

## 5. API WebSocket

### Connexion au Serveur

```javascript
// JavaScript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    console.log('Connecté au serveur de monitoring');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Données reçues:', data);
};

ws.onerror = (error) => {
    console.error('Erreur WebSocket:', error);
};
```

```python
# Python avec websockets
import asyncio
import websockets
import json

async def client():
    async with websockets.connect('ws://localhost:8765') as websocket:
        while True:
            data = await websocket.recv()
            message = json.loads(data)
            print(f"Reçu: {message}")

asyncio.run(client())
```

### Format des Messages

#### Alertes dans les Messages WebSocket

Les alertes sont automatiquement incluses dans les messages de monitoring lorsque les seuils configurés sont dépassés. Le champ `alerts` est un tableau optionnel qui contient :

- **timestamp** : Horodatage de l'alerte au format ISO 8601
- **component** : Composant concerné (`memory` ou `disk`)
- **metric** : Métrique qui a déclenché l'alerte (`usage_percent`)
- **value** : Valeur actuelle de la métrique
- **threshold** : Seuil qui a été dépassé
- **level** : Niveau d'alerte (`WARNING` ou `CRITICAL`)
- **message** : Message descriptif de l'alerte

Les seuils par défaut sont :
- Mémoire : WARNING à 80%, CRITICAL à 90%
- Disque : WARNING à 85%, CRITICAL à 95%

#### Message de Monitoring

```json
{
  "type": "monitoring_data",
  "timestamp": "2025-01-03T10:15:30.123456",
  "data": {
    "memory": {
      "total": 17179869184,
      "available": 8589934592,
      "used": 8589934592,
      "percentage": 50.0
    },
    "processor": {
      "usage_percent": 25.5,
      "core_count": 4,
      "logical_count": 8,
      "frequency_current": 2495.0,
      "frequency_max": 3700.0,
      "per_core_usage": [20.1, 30.2, 15.5, 40.0]
    },
    "disk": {
      "total": 500107862016,
      "used": 250053931008,
      "free": 250053931008,
      "percentage": 50.0,
      "path": "/"
    },
    "system": {
      "os_name": "Windows",
      "os_version": "10.0.19045",
      "os_release": "10",
      "architecture": "AMD64",
      "machine": "AMD64",
      "processor": "Intel64 Family 6 Model 142 Stepping 10",
      "hostname": "DESKTOP-ABC123",
      "python_version": "3.11.5",
      "processes": 250,
      "boot_time": "2025-01-01T08:00:00"
    },
    "gpu": {
      "count": 1,
      "gpus": [
        {
          "id": 0,
          "name": "NVIDIA GeForce RTX 3080",
          "driver_version": "537.58",
          "memory_total": 10737418240,
          "memory_used": 5368709120,
          "memory_free": 5368709120,
          "gpu_usage_percent": 45.0,
          "temperature": 65.0,
          "power_draw": 220.5,
          "power_limit": 350.0
        }
      ]
    }
  },
  "alerts": [
    {
      "timestamp": "2025-01-03T10:15:30.123456",
      "component": "memory",
      "metric": "usage_percent",
      "value": 85.5,
      "threshold": 80.0,
      "level": "WARNING",
      "message": "High memory usage: 85.5% (threshold: 80.0%)"
    },
    {
      "timestamp": "2025-01-03T10:15:30.123456",
      "component": "disk",
      "metric": "usage_percent",
      "value": 96.2,
      "threshold": 95.0,
      "level": "CRITICAL",
      "message": "Critical disk usage: 96.2% (threshold: 95.0%)"
    }
  ]
}
```

#### Messages de Contrôle

**Ping/Pong :**
```json
// Client envoie
{"type": "ping"}

// Serveur répond
{"type": "pong", "timestamp": "2025-01-03T10:15:30.123456"}
```

**Statut du Serveur :**
```json
// Client envoie
{"type": "get_status"}

// Serveur répond
{
  "type": "status",
  "connected_clients": 5,
  "server_start_time": "2025-01-03T10:00:00.000000",
  "message": "Server is running"
}
```

**Messages d'Erreur :**
```json
{
  "type": "error",
  "message": "Invalid message format",
  "code": "INVALID_FORMAT"
}
```

### Gestion des Alertes côté Client

Exemple JavaScript pour traiter les alertes reçues :

```javascript
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    if (message.type === 'monitoring_data') {
        // Traiter les données de monitoring
        updateMetrics(message.data);
        
        // Vérifier et traiter les alertes
        if (message.alerts && message.alerts.length > 0) {
            message.alerts.forEach(alert => {
                if (alert.level === 'CRITICAL') {
                    console.error(`🚨 CRITICAL: ${alert.message}`);
                    // Afficher une notification urgente
                    showCriticalNotification(alert);
                } else if (alert.level === 'WARNING') {
                    console.warn(`⚠️ WARNING: ${alert.message}`);
                    // Afficher un avertissement
                    showWarningNotification(alert);
                }
            });
        }
    }
};
```

### Commandes Disponibles

| Commande | Description | Réponse | Exemple |
|----------|-------------|---------|----------|
| `ping` | Test de connectivité | `pong` avec timestamp | `{"type": "ping"}` |
| `get_status` | État du serveur | Informations serveur | `{"type": "get_status"}` |
| `subscribe` | S'abonner aux mises à jour | Confirmation d'abonnement | `{"type": "subscribe"}` |
| `unsubscribe` | Se désabonner | Confirmation de désabonnement | `{"type": "unsubscribe"}` |

**Protocole WebSocket Complet :**

```python
# Messages de contrôle supportés
messages = {
    # Client -> Serveur
    "ping": {"type": "ping"},
    "get_status": {"type": "get_status"},
    "subscribe": {"type": "subscribe"},
    "unsubscribe": {"type": "unsubscribe"},
    
    # Serveur -> Client
    "connection": {"type": "connection", "status": "connected"},
    "monitoring_data": {"type": "monitoring_data", "data": {...}},
    "pong": {"type": "pong", "timestamp": "..."},
    "status": {"type": "status", "server_version": "...", ...},
    "error": {"type": "error", "message": "...", "code": "..."}
}

# Gestion des timeouts et limites
- Envoi WebSocket : 1 seconde
- Broadcast : Semaphore limité à 50 concurrents
- Reconnexion automatique : Non implémentée côté serveur
- Limite clients : 1000 par défaut (configurable)
```

## 6. Métriques Collectées

### Processeur (CPU)

| Métrique | Description | Unité |
|----------|-------------|-------|
| `usage_percent` | Utilisation globale | % |
| `per_core_usage` | Utilisation par cœur | % |
| `core_count` | Cœurs physiques | nombre |
| `logical_count` | Cœurs logiques | nombre |
| `frequency_current` | Fréquence actuelle | MHz |
| `frequency_max` | Fréquence maximale | MHz |

### Mémoire RAM

| Métrique | Description | Unité |
|----------|-------------|-------|
| `total` | Mémoire totale | octets |
| `available` | Mémoire disponible | octets |
| `used` | Mémoire utilisée | octets |
| `percentage` | Pourcentage utilisé | % |

### Disque

| Métrique | Description | Unité |
|----------|-------------|-------|
| `total` | Espace total | octets |
| `used` | Espace utilisé | octets |
| `free` | Espace libre | octets |
| `percentage` | Pourcentage utilisé | % |
| `path` | Chemin surveillé | string |

### GPU (si disponible)

| Métrique | Description | Unité |
|----------|-------------|-------|
| `name` | Nom du GPU | string |
| `driver_version` | Version du driver | string |
| `memory_total` | Mémoire totale | octets |
| `memory_used` | Mémoire utilisée | octets |
| `memory_free` | Mémoire libre | octets |
| `gpu_usage_percent` | Utilisation GPU | % |
| `temperature` | Température | °C |
| `power_draw` | Consommation actuelle | W |
| `power_limit` | Limite de puissance | W |

## 7. Système d'Alertes

### Configuration des Seuils

```python
from services.realtime import RealtimeMonitoringService
from alerts.alert_handlers import ConsoleAlertHandler, FileAlertHandler

# Créer le service de monitoring
service = RealtimeMonitoringService()

# Configurer les seuils d'alerte
service.alert_manager.set_threshold('memory', 'warning', 75)
service.alert_manager.set_threshold('memory', 'critical', 85)
service.alert_manager.set_threshold('disk', 'warning', 80)
service.alert_manager.set_threshold('disk', 'critical', 95)
# Note: CPU n'est pas dans les composants valides (seulement memory et disk)

# Ajouter des handlers d'alertes
service.alert_manager.add_handler(ConsoleAlertHandler())
service.alert_manager.add_handler(FileAlertHandler("./alerts.log"))
```

### Types d'Alertes

1. **WARNING** : Seuil d'avertissement dépassé
2. **CRITICAL** : Seuil critique dépassé

### Handlers d'Alertes Disponibles

#### ConsoleAlertHandler
Affiche les alertes dans la console avec couleurs :
- Jaune pour WARNING
- Rouge pour CRITICAL

```python
from alerts.handlers import ConsoleAlertHandler
handler = ConsoleAlertHandler(name="console")
```

#### FileAlertHandler
Enregistre les alertes dans un fichier :

```python
from alerts.handlers import FileAlertHandler
handler = FileAlertHandler(name="file", log_file="./monitoring_alerts.log")
```

#### EmailAlertHandler
Envoie les alertes par email :

```python
from alerts.handlers import EmailAlertHandler

handler = EmailAlertHandler(
    name="email",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="monitoring@example.com",
    password="app_password",
    from_email="monitoring@example.com",
    to_emails=["admin@example.com", "ops@example.com"],
    use_tls=True
)
```

#### FileAlertHandler Avancé
Rotation automatique des logs à 10MB :

```python
from alerts.alert_handlers import FileAlertHandler

# Rotation automatique des fichiers de log
handler = FileAlertHandler(
    log_file="./monitoring_alerts.log",
    max_file_size=10*1024*1024  # 10MB
)
```

#### WebhookAlertHandler
Envoie les alertes vers un webhook HTTP/HTTPS :

```python
from alerts.handlers import WebhookAlertHandler

handler = WebhookAlertHandler(
    name="webhook",
    webhook_url="https://api.example.com/webhook/alerts",
    headers={"Authorization": "Bearer token123"},
    timeout=10
)
```

#### SlackAlertHandler
Intégration native avec Slack :

```python
from alerts.handlers import SlackAlertHandler

handler = SlackAlertHandler(
    name="slack",
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    channel="#monitoring",  # Optionnel
    username="MonitoringBot"
)
# Note: Les emojis et couleurs sont gérés automatiquement selon le niveau d'alerte
```

### Filtres d'Alertes

```python
from alerts.handlers import create_level_filter, create_component_filter, create_time_filter

# Filtre par niveau minimum
from core.enums import AlertLevel
level_filter = create_level_filter(AlertLevel.WARNING)

# Filtre par composants
component_filter = create_component_filter(
    allowed_components=["memory", "cpu"]
)

# Filtre par plage horaire (supporte les plages traversant minuit)
time_filter = create_time_filter(
    start_hour=9,
    end_hour=18,
    timezone="Europe/Paris"
)

# Appliquer les filtres
handler.add_filter(level_filter)
handler.add_filter(component_filter)
handler.add_filter(time_filter)
```

##### Gestionnaire de Handlers

```python
from alerts.handlers import AlertHandlerManager

# Créer un gestionnaire centralisé
manager = AlertHandlerManager()

# Ajouter plusieurs handlers
console_handler = ConsoleAlertHandler()
file_handler = FileAlertHandler("alerts.log")
slack_handler = SlackAlertHandler(webhook_url="...")

manager.add_handler(console_handler)
manager.add_handler(file_handler)
manager.add_handler(slack_handler)

# Méthodes de gestion
manager.list_handlers()  # Liste tous les handlers
handler = manager.get_handler("file")  # Récupère un handler spécifique

# Récupérer et gérer des handlers spécifiques
file_handler = manager.get_handler("file")
if file_handler:
    file_handler.enabled = False  # Désactiver
    file_handler.enabled = True   # Réactiver

# Supprimer un handler
manager.remove_handler("file")

# Opérations groupées
manager.enable_all()
manager.disable_all()
manager.clear_all()

# Distribuer une alerte
results = manager.handle_alert(alert)
for handler_name, success in results.items():
    print(f"{handler_name}: {'Succès' if success else 'Échec'}")

# Obtenir des statistiques
stats = manager.get_statistics()
print(f"Alertes traitées: {stats['total_handled']}")
print(f"Erreurs: {stats['total_errors']}")
```

### Méthodes Avancées des Handlers

```python
# Gestion des filtres
handler.add_filter(my_filter)
handler.remove_filter(my_filter)
handler.clear_filters()

# Vérification manuelle
if handler.should_handle(alert):
    handler.handle(alert)

# Accès aux compteurs (avec protection anti-overflow)
print(f"Alertes traitées: {handler.handled_count}")
print(f"Erreurs: {handler.error_count}")
```

### Callbacks Personnalisés

```python
def custom_alert_callback(alert):
    print(f"Alerte personnalisée: {alert.level} - {alert.message}")
    # Envoyer à un système externe, SMS, Slack, etc.

service.alert_manager.add_alert_callback(custom_alert_callback)
```

### Cooldown des Alertes

Pour éviter le spam, un système de cooldown est intégré :
- Délai par défaut : 300 secondes (5 minutes)
- Configurable par type d'alerte

```python
# Modifier le cooldown global (pas par composant)
service.alert_manager.cooldown_seconds = 600  # 10 minutes
```

## 8. Utilisation Avancée

### Méthodes Avancées du Service

```python
from services.realtime import RealtimeMonitoringService

service = RealtimeMonitoringService()
service.start()

# Obtenir un résumé formaté de l'état système
summary = service.get_system_summary()
print(summary)

# Récupérer l'historique avec limite
history = service.get_snapshots_history(count=100)

# Forcer un export immédiat (méthode asynchrone)
import asyncio
asyncio.run(service.force_export())

# Configurer dynamiquement les seuils
service.configure_thresholds({
    'memory_warning': 70,
    'memory_critical': 85,
    'disk_warning': 80,
    'disk_critical': 90
})

# Obtenir un rapport de santé complet
health_report = service.get_health_report()
print(f"Santé du service: {health_report['service']['status']}")
print(f"Uptime: {health_report['service']['uptime_seconds']}s")
print(f"Statistiques: {health_report['statistics']}")
```

### Paramètres Avancés de Configuration

```python
from services.realtime import RealtimeMonitoringService

# Configuration avancée du service (paramètres directs)
from pathlib import Path

service = RealtimeMonitoringService(
    monitor_interval=0.5,
    export_interval=60.0,
    max_snapshots_history=1000,
    export_dir=Path("./monitoring_data"),
    max_workers=8  # Nombre de workers ThreadPoolExecutor
)

# Accès aux propriétés du service
print(f"Status: {service.status}")
print(f"En cours: {service.is_running}")
snapshot = service.current_snapshot  # Propriété, pas méthode

# Méthodes d'accès à l'historique
history = service.get_snapshots_history()  # Historique complet
recent = service.get_snapshots_history(count=50)  # Derniers N snapshots
```

### Mode Thread-Safe

Pour une utilisation dans des applications multi-thread :

```python
from services.threadsafe import ThreadSafeMonitoringService

# Créer un service thread-safe avec configuration avancée
service = ThreadSafeMonitoringService(
    data_queue_size=100  # Taille de la queue (défaut: 100)
)
service.start()

# Utilisation depuis plusieurs threads
def worker_thread():
    while True:
        data = service.get_current_data()
        if data:
            print(f"CPU: {data['cpu']['usage_percent']}%")
            print(f"Mémoire: {data['memory']['usage_percent']}%")
        time.sleep(1)

# Lancer plusieurs threads
threads = []
for i in range(5):
    t = threading.Thread(target=worker_thread)
    t.start()
    threads.append(t)
```

### Export Personnalisé

#### Créer un Exporter Personnalisé

```python
from exporters.base import BaseExporter
from typing import Dict, Any

class CustomExporter(BaseExporter):
    def export(self, data: Dict[str, Any]) -> None:
        # Votre logique d'export personnalisée
        print(f"Export personnalisé: {data}")
    
    def initialize(self) -> None:
        print("Initialisation de l'exporter personnalisé")
    
    def cleanup(self) -> None:
        print("Nettoyage de l'exporter personnalisé")

# Utiliser l'exporter personnalisé
# Note: RealtimeMonitoringService utilise un seul exporter (JSONExporter par défaut)
# Pour un exporter personnalisé, il faudrait modifier le code source du service
```

#### WebSocketExporter Intégré

```python
from exporters.websocket_exporter import WebSocketExporter

# Créer un exporter WebSocket pour intégration personnalisée
ws_exporter = WebSocketExporter(
    host="0.0.0.0",
    port=8765,
    export_interval=1.0
)

# Méthodes disponibles
ws_exporter.start_server()  # Démarrer le serveur dans un thread séparé
ws_exporter.stop_server()   # Arrêter le serveur
info = ws_exporter.get_export_info()  # Obtenir les infos d'export

# Note: RealtimeMonitoringService n'a pas de liste d'exporters
# Il utilise un seul exporter configuré à l'initialisation
```

#### Options Avancées JSONExporter

```python
from exporters.json_exporter import JSONExporter
from pathlib import Path

# Configuration avancée de l'export JSON
json_exporter = JSONExporter(
    output_dir=Path("./monitoring_data"),
    compress=True,          # Compression gzip
    pretty_print=True,      # JSON indenté
    date_in_filename=True   # Format: monitoring_20250103.json ou .json.gz
)
# Note: Pas de paramètre export_interval ou max_file_size dans JSONExporter
```

#### Méthodes WebSocketExporter

```python
from exporters.websocket_exporter import WebSocketExporter

# Méthodes spécifiques du WebSocketExporter
ws_exporter = WebSocketExporter()

# Export d'un snapshot unique (async)
await ws_exporter.export_snapshot(snapshot)

# Le destructeur arrête automatiquement le serveur
# lors de la suppression de l'objet (méthode __del__)
```

### Monitoring Sélectif

```python
from monitors import create_system_monitor

# Créer un moniteur avec seulement certains composants
monitor = create_system_monitor(
    enable_processor=True,
    enable_memory=True,
    enable_disk=False,  # Désactiver le monitoring disque
    enable_gpu=False    # Désactiver le monitoring GPU
)

# Utiliser le moniteur
data = monitor.collect()
print(f"CPU: {data['processor']['usage_percent']}%")
print(f"RAM: {data['memory']['percentage']}%")
```

### Utilitaires GPU Avancés

```python
from monitors.gpu import GPUMonitor

# Utilisation du GPU Monitor
monitor = GPUMonitor()

# Vérifier la disponibilité GPU
if monitor.is_available():
    # Collecter les données GPU
    gpu_data = monitor.collect()
    if gpu_data:
        print(f"Nombre de GPUs: {gpu_data['count']}")
        for gpu in gpu_data['gpus']:
            print(f"GPU {gpu['id']}: {gpu['name']}")
            print(f"  Mémoire: {gpu['memory_used']}/{gpu['memory_total']} MB")
            print(f"  Utilisation: {gpu['gpu_usage_percent']}%")
            print(f"  Température: {gpu['temperature']}°C")

# Détection des backends GPU (ordre de priorité)
# 1. GPUtil (le plus simple)
# 2. pynvml/nvidia-ml-py3 (accès direct NVML)
# 3. nvidia-smi XML parsing (fallback)

monitor = GPUMonitor()
info = monitor.get_gpu_info()  # Alias pour get_data()
```

### Monitoring Mémoire du Service

```python
from monitors.service_memory import ServiceMemoryMonitor

# Créer un moniteur de mémoire interne
memory_monitor = ServiceMemoryMonitor()

# Obtenir les statistiques actuelles
stats = memory_monitor.get_current_stats()
print(f"Mémoire RSS: {stats['rss'] / (1024**2):.1f} MB")
print(f"Utilisation: {stats['percent']:.1f}%")
print(f"Threads actifs: {stats['thread_count']}")
print(f"Fichiers ouverts: {stats['open_files']}")
print(f"Connexions: {stats['connections']}")
print(f"Collections GC: {stats['gc_collections']}")  # (gen0, gen1, gen2)

# Analyser la tendance mémoire
trend = memory_monitor.get_memory_trend(minutes=60)  # Dernière heure
if trend.get('status') == 'ok':
    print(f"Croissance: {trend['growth_rate_per_hour'] / (1024**2):.1f} MB/heure")
    print(f"Mémoire moyenne: {trend['average_memory'] / (1024**2):.1f} MB")

# Vérifier la santé mémoire
is_healthy, warnings = memory_monitor.check_memory_health()
if not is_healthy:
    print(f"Problèmes mémoire détectés:")
    for warning in warnings:
        print(f"  - {warning}")
    
# Forcer le garbage collection
result = memory_monitor.force_garbage_collection()
print(f"Mémoire libérée: {result['memory_freed'] / (1024**2):.1f} MB")
print(f"Objets collectés: {result['objects_collected']}")

# Résumé complet
summary = memory_monitor.get_summary()
print(summary)
```

### Gestionnaire d'Affichage

```python
from utils.display import DisplayManager

# Créer un gestionnaire d'affichage
display = DisplayManager(
    clear_screen=True,  # Clear screen entre les mises à jour
    compact_mode=False  # Mode détaillé
)

# Vérifier si le clear screen est supporté
if display.clear_supported:
    display.clear_screen()

# Méthodes d'affichage disponibles
display.print_header("MON MONITORING CUSTOM")  # En-tête
display.print_separator("-", 80)  # Ligne de séparation

# Mode compact (pour IDE)
display.print_compact_header(iteration=1, timestamp="2025-01-03 10:15:30")
display.print_compact_metrics(data)  # Une ligne avec emojis

# Mode détaillé
display.print_detailed_metrics(data)

# Sections spécialisées  
display.print_alerts_section(alerts, recent_alerts)
display.print_statistics_section(stats)

# Note: DisplayManager n'a pas de propriété 'compact_mode' ni de méthode 'show_metrics'
```

### Modification Dynamique de Configuration

```python
# Les constantes de config.py sont utilisées à l'initialisation
# Pour modifier dynamiquement, passez les valeurs aux constructeurs

from services.realtime import RealtimeMonitoringService

# Créer un service avec des valeurs personnalisées
service = RealtimeMonitoringService(
    monitor_interval=2.0,      # Au lieu de MONITOR_INTERVAL
    export_interval=120.0,     # Au lieu de EXPORT_INTERVAL
    max_snapshots_history=500  # Au lieu de MAX_SNAPSHOTS_HISTORY
)

# Pour des changements permanents, modifiez directement config.py
```

### Historique et Statistiques

```python
from services.realtime import RealtimeMonitoringService
import statistics

service = RealtimeMonitoringService()
service.start()

# Attendre quelques secondes pour collecter des données
time.sleep(30)

# Obtenir l'historique
history = service.get_snapshot_history(limit=60)

# Calculer des statistiques
cpu_values = [s.processor_info.usage_percent for s in history if s.processor_info]
memory_values = [s.memory_info.percentage for s in history if s.memory_info]

print(f"CPU - Moyenne: {statistics.mean(cpu_values):.2f}%")
print(f"CPU - Max: {max(cpu_values):.2f}%")
print(f"Mémoire - Moyenne: {statistics.mean(memory_values):.2f}%")
print(f"Mémoire - Max: {max(memory_values):.2f}%")
```

### Détection Améliorée de Fréquence CPU

```python
from monitors.processor import get_cpu_max_frequency, get_cpu_current_frequency

# Utilise des méthodes avancées adaptées à chaque OS (Windows, Linux, macOS)
max_freq = get_cpu_max_frequency()
current_freq = get_cpu_current_frequency()

print(f"Fréquence maximale: {max_freq} MHz")
print(f"Fréquence actuelle: {current_freq} MHz")

# Note: Le script principal contient des versions simplifiées de ces fonctions
# qui utilisent principalement psutil pour éviter les conflits d'imports
```

## 9. Intégration

### Intégration avec FastAPI

```python
from fastapi import FastAPI, WebSocket
from services.realtime import RealtimeMonitoringService
import asyncio
import json

app = FastAPI()
monitoring_service = RealtimeMonitoringService()

@app.on_event("startup")
async def startup():
    monitoring_service.start()

@app.on_event("shutdown")
async def shutdown():
    monitoring_service.stop()

@app.websocket("/ws/monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            snapshot = monitoring_service.current_snapshot
            if snapshot:
                await websocket.send_json(snapshot.to_dict())
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Erreur WebSocket: {e}")
    finally:
        await websocket.close()

@app.get("/api/monitoring/current")
async def get_current_metrics():
    snapshot = monitoring_service.current_snapshot
    return snapshot.to_dict() if snapshot else {"error": "No data available"}
```

### Intégration avec Flask

```python
from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
from services.realtime import RealtimeMonitoringService
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
monitoring_service = RealtimeMonitoringService()

def background_thread():
    """Thread pour envoyer les données de monitoring"""
    while True:
        time.sleep(1)
        snapshot = monitoring_service.current_snapshot
        if snapshot:
            socketio.emit('monitoring_update', snapshot.to_dict())

@app.route('/api/monitoring')
def get_monitoring_data():
    snapshot = monitoring_service.current_snapshot
    return jsonify(snapshot.to_dict() if snapshot else {})

@socketio.on('connect')
def handle_connect():
    print('Client connecté')
    emit('connected', {'data': 'Connected to monitoring server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client déconnecté')

if __name__ == '__main__':
    monitoring_service.start()
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5000)
```

### Intégration avec Django

```python
# monitoring/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from services.realtime import RealtimeMonitoringService
import asyncio

class MonitoringConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitoring_service = RealtimeMonitoringService()
        self.monitoring_task = None

    async def connect(self):
        await self.accept()
        self.monitoring_service.start()
        self.monitoring_task = asyncio.create_task(self.send_monitoring_data())

    async def disconnect(self, close_code):
        if self.monitoring_task:
            self.monitoring_task.cancel()
        self.monitoring_service.stop()

    async def send_monitoring_data(self):
        while True:
            try:
                snapshot = self.monitoring_service.get_latest_snapshot()
                if snapshot:
                    await self.send(text_data=json.dumps({
                        'type': 'monitoring_data',
                        'data': snapshot.to_dict()
                    }))
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Erreur lors de l'envoi des données: {e}")

# monitoring/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/monitoring/$', consumers.MonitoringConsumer.as_asgi()),
]
```

### Intégration avec Prometheus

```python
from prometheus_client import Gauge, start_http_server
from services.realtime import RealtimeMonitoringService
import time

# Créer les métriques Prometheus
cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('system_memory_usage_percent', 'Memory usage percentage')
disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage')
gpu_usage = Gauge('system_gpu_usage_percent', 'GPU usage percentage', ['gpu_id'])
gpu_memory = Gauge('system_gpu_memory_usage_percent', 'GPU memory usage percentage', ['gpu_id'])
gpu_temp = Gauge('system_gpu_temperature_celsius', 'GPU temperature in Celsius', ['gpu_id'])

def update_prometheus_metrics():
    service = RealtimeMonitoringService()
    service.start()
    
    while True:
        snapshot = service.get_latest_snapshot()
        if snapshot:
            # CPU
            if snapshot.processor:
                cpu_usage.set(snapshot.processor.usage_percent)
            
            # Mémoire
            if snapshot.memory:
                memory_usage.set(snapshot.memory.percentage)
            
            # Disque
            if snapshot.disk:
                disk_usage.set(snapshot.disk.percentage)
            
            # GPU
            if snapshot.gpu and snapshot.gpu.gpus:
                for gpu in snapshot.gpu.gpus:
                    gpu_usage.labels(gpu_id=str(gpu.id)).set(gpu.usage_percent)
                    if gpu.memory_total > 0:
                        gpu_memory_percent = (gpu.memory_used / gpu.memory_total) * 100
                        gpu_memory.labels(gpu_id=str(gpu.id)).set(gpu_memory_percent)
                    if gpu.temperature is not None:
                        gpu_temp.labels(gpu_id=str(gpu.id)).set(gpu.temperature)
        
        time.sleep(5)  # Mise à jour toutes les 5 secondes

if __name__ == '__main__':
    # Démarrer le serveur HTTP Prometheus sur le port 8000
    start_http_server(8000)
    print("Serveur Prometheus démarré sur http://localhost:8000")
    update_prometheus_metrics()
```

### Intégration avec Bases de Données

#### Export vers InfluxDB

```python
from exporters.base import BaseExporter
from influxdb_client import InfluxDBClient, Point
from typing import Dict, Any

class InfluxDBExporter(BaseExporter):
    def __init__(self, url, token, org, bucket, export_interval=10):
        super().__init__(export_interval)
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api()
        self.bucket = bucket
        self.org = org
    
    def export(self, data: Dict[str, Any]) -> None:
        snapshot = data.get('snapshot')
        if not snapshot:
            return
            
        # Créer les points de données
        points = []
        
        # CPU
        if snapshot.processor:
            point = Point("cpu") \
                .field("usage_percent", snapshot.processor.usage_percent) \
                .field("frequency_current", snapshot.processor.frequency_current)
            points.append(point)
        
        # Mémoire
        if snapshot.memory:
            point = Point("memory") \
                .field("percentage", snapshot.memory.percentage) \
                .field("used", snapshot.memory.used) \
                .field("available", snapshot.memory.available)
            points.append(point)
        
        # Écrire dans InfluxDB
        self.write_api.write(bucket=self.bucket, org=self.org, record=points)
    
    def cleanup(self) -> None:
        self.client.close()

# Utilisation avec un exporter personnalisé
# Note: RealtimeMonitoringService utilise JSONExporter par défaut
# Pour utiliser InfluxDBExporter, il faudrait modifier le code du service
# ou créer un service personnalisé qui utilise cet exporter

influx_exporter = InfluxDBExporter(
    url="http://localhost:8086",
    token="your-token",
    org="your-org",
    bucket="monitoring"
)
```

#### Export vers PostgreSQL/MySQL

```python
import psycopg2  # ou pymysql pour MySQL
from datetime import datetime

class DatabaseExporter(BaseExporter):
    def __init__(self, connection_params, export_interval=60):
        super().__init__(export_interval)
        self.connection_params = connection_params
        self._init_database()
    
    def _init_database(self):
        # Créer les tables si elles n'existent pas
        conn = psycopg2.connect(**self.connection_params)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_snapshots (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                cpu_usage FLOAT,
                memory_usage FLOAT,
                disk_usage FLOAT,
                gpu_usage FLOAT,
                data JSONB
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def export(self, data: Dict[str, Any]) -> None:
        snapshot = data.get('snapshot')
        if not snapshot:
            return
        
        conn = psycopg2.connect(**self.connection_params)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO monitoring_snapshots 
            (timestamp, cpu_usage, memory_usage, disk_usage, gpu_usage, data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datetime.now(),
            snapshot.processor.usage_percent if snapshot.processor else None,
            snapshot.memory.percentage if snapshot.memory else None,
            snapshot.disk.percentage if snapshot.disk else None,
            snapshot.gpu.gpus[0].usage_percent if snapshot.gpu and snapshot.gpu.gpus else None,
            json.dumps(snapshot.to_dict())
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
```

## 10. Architecture


### Structure du Projet

```
monitoring-websocket-system-server/
├── core/                       # Cœur du système
│   ├── __init__.py
│   ├── models.py              # Modèles de données (snapshots, infos, alertes)
│   ├── enums.py               # Énumérations (AlertLevel, etc.)
│   └── exceptions.py          # Exceptions personnalisées
│
├── monitors/                   # Collecteurs de métriques
│   ├── __init__.py
│   ├── base.py                # Classe de base abstraite
│   ├── processor.py           # Monitoring CPU
│   ├── memory.py              # Monitoring RAM
│   ├── disk.py                # Monitoring disque
│   ├── gpu.py                 # Monitoring GPU avec détection intégrée
│   ├── system.py              # Moniteur système complet
│   ├── service_memory.py      # Monitoring mémoire interne du service
│   └── factory.py             # Factory pour création des moniteurs
│
├── services/                   # Services principaux
│   ├── __init__.py
│   ├── realtime.py            # Service de monitoring temps réel
│   ├── threadsafe.py          # Version thread-safe
│   └── websocket_server.py    # Serveur WebSocket
│
├── exporters/                  # Export des données
│   ├── __init__.py
│   ├── base.py                # Classe de base abstraite
│   ├── json_exporter.py       # Export JSON avec rotation
│   ├── websocket_exporter.py  # Export WebSocket broadcast
│   └── factory.py             # Factory pour création des exporters
│
├── alerts/                     # Système d'alertes
│   ├── __init__.py
│   ├── manager.py             # Gestionnaire d'alertes
│   └── handlers.py            # Handlers (console, file, email, webhook, slack)
│
├── utils/                      # Utilitaires
│   ├── __init__.py
│   ├── display.py             # Gestion affichage console
│   ├── formatters.py          # Formatage complet (tables, progress bars, etc.)
│   └── system.py              # Utilitaires système
│
├── pypi/                       # Scripts de publication PyPI
│   ├── publish_pypi.bat
│   └── publish_pypitest.bat
│
├── config.py                   # Constantes de configuration centralisées
├── run_server.py              # Script principal du serveur WebSocket avec options CLI
├── requirements.txt           # Dépendances Python
├── setup.py                   # Configuration package
├── pyproject.toml             # Configuration moderne Python
├── MANIFEST.in                # Manifest package
├── README.md                  # Documentation principale
└── CLAUDE.md                  # Instructions pour Claude Code
```

### Diagramme d'Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              MONITORING WEBSOCKET SERVER                               │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                    DATA COLLECTION LAYER                         │  │
│  │                                                                                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │
│  │  │   CPU/Core  │  │   Memory    │  │    Disk     │  │     GPU     │              │  │
│  │  │   Monitor   │  │   Monitor   │  │   Monitor   │  │   Monitor   │              │  │
│  │  │             │  │             │  │             │  │             │              │  │
│  │  │ • Usage %   │  │ • Total     │  │ • Total     │  │ • Usage %   │              │  │
│  │  │ • Frequency │  │ • Used      │  │ • Free      │  │ • Memory    │              │  │
│  │  │ • Cores     │  │ • Available │  │ • Used %    │  │ • Temp °C   │              │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │  │
│  │         │                │                │                │                     │  │
│  │         └────────────────┴────────────────┴────────────────┘                     │  │
│  │                                      │                                           │  │
│  │                                      ▼                                           │  │
│  │                            ┌───────────────────┐                                 │  │
│  │                            │   System Monitor  │                                 │  │
│  │                            │   (Aggregator)    │                                 │  │
│  │                            └───────────┬───────┘                                 │  │
│  └────────────────────────────────────────┴─────────────────────────────────────────┘  │
│                                           │                                            │
│  ┌────────────────────────────────────────┴─────────────────────────────────────────┐  │
│  │                                 PROCESSING & ANALYSIS LAYER                      │  │
│  │                                                                                  │  │
│  │    ┌─────────────────────┐         ┌──────────────────────┐                      │  │
│  │    │  Realtime Service   │         │   Alert Manager      │                      │  │
│  │    │                     │         │                      │                      │  │
│  │    │ • Data Collection   │◄────────┤ • Threshold Check    │                      │  │
│  │    │ • History (1000)    │         │ • Alert Generation   │                      │  │
│  │    │ • Thread Pool       │         │ • Cooldown (5min)    │                      │  │
│  │    │ • Export Scheduling │         │ • Handler Dispatch   │                      │  │
│  │    └──────────┬──────────┘         └──────────┬───────────┘                      │  │
│  │               │                               │                                  │  │
│  │               │                   ┌───────────┴────────────┐                     │  │
│  │               │                   ▼                        ▼                     │  │
│  │               │         ┌─────────────────┐      ┌──────────────────┐            │  │
│  │               │         │ Console Handler │      │  File Handler    │            │  │
│  │               │         │ (Color Output)  │      │ (Log Rotation)   │            │  │
│  │               │         └─────────────────┘      └──────────────────┘            │  │
│  │               │                                                                  │  │
│  │               │         ┌─────────────────┐      ┌──────────────────┐            │  │
│  │               │         │ Email Handler   │      │ Webhook Handler  │            │  │
│  │               │         │ (SMTP)          │      │ (HTTP/HTTPS)     │            │  │ 
│  │               │         └─────────────────┘      └──────────────────┘            │  │
│  │               │                                                                  │  │
│  │               │                      ┌──────────────────┐                        │  │
│  │               │                      │  Slack Handler   │                        │  │
│  │               │                      │ (Webhook API)    │                        │  │
│  │               │                      └──────────────────┘                        │  │
│  └───────────────┴──────────────────────────────────────────────────────────────────┘  │
│                  │                                                                     │
│  ┌───────────────┴──────────────────────────────────────────────────────────────────┐  │
│  │                               DATA DISTRIBUTION LAYER                            │  │
│  │                                                                                  │  │
│  │    ┌─────────────────────┐                    ┌───────────────────────┐          │  │
│  │    │   JSON Exporter     │                    │  WebSocket Server     │          │  │
│  │    │                     │                    │                       │          │  │
│  │    │ • File Rotation     │                    │ • Port 8765           │          │  │
│  │    │ • Compression       │                    │ • Max 1000 clients    │          │  │
│  │    │ • Timestamping      │                    │ • Broadcast (50/sec)  │          │  │
│  │    └─────────────────────┘                    │ • Control Commands    │          │  │
│  │                                               └───────────┬───────────┘          │  │
│  └───────────────────────────────────────────────────────────┴──────────────────────┘  │
│                                                              │                         │
│                                                              ▼                         │
│                                              ┌─────────────────────────────┐           │
│                                              │   WebSocket Clients         │           │
│                                              │                             │           │
│                                              │ • Real-time monitoring      │           │
│                                              │ • Alert notifications       │           │
│                                              │ • Control messages          │           │
│                                              └─────────────────────────────┘           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Flux de Données

1. **Collecte** : Les monitors collectent les métriques système
   - Collecte parallèle via ThreadPoolExecutor
   - Nettoyage automatique de l'historique (TTL 1 heure)
   - Thread naming avec préfixe "monitoring-"

2. **Agrégation** : Le service agrège les données dans un snapshot
   - Protection contre les race conditions
   - Gestion automatique des overflows de compteurs
   - Limites: 10M alertes, 1M erreurs

3. **Distribution** : 
   - Export vers fichiers JSON (avec rotation)
   - Diffusion via WebSocket (broadcast limité)
   - Déclenchement d'alertes (avec cooldown)
   
4. **Consommation** : Les clients reçoivent les données en temps réel
   - Format JSON structuré
   - Messages d'erreur typés
   - Gestion automatique des déconnexions

### Patterns de Conception

- **Factory Pattern** : Création dynamique des monitors et exporters (monitors/factory.py, exporters/factory.py)
- **Observer Pattern** : Système d'alertes avec callbacks
- **Module Pattern** : Configuration centralisée via constantes (config.py)
- **Strategy Pattern** : Différentes stratégies d'export (JSON, WebSocket)
- **Template Method** : Classes de base abstraites (base.py dans monitors et exporters)
- **Handler Pattern** : Gestion modulaire des alertes (ConsoleHandler, FileHandler, EmailHandler, WebhookHandler, SlackHandler)

### Nouveaux Composants

#### Détection de Fréquence CPU
Les fonctions de détection de fréquence CPU sont intégrées dans `monitors/processor.py` :
- `get_cpu_max_frequency()` : Détecte la fréquence maximale du CPU
- `get_cpu_current_frequency()` : Détecte la fréquence actuelle du CPU
- Implémentations spécifiques pour Windows, Linux et macOS
- Fallback automatique sur plusieurs méthodes de détection
- Gestion des valeurs incorrectes retournées par psutil
- Le script principal contient des versions simplifiées de ces fonctions pour éviter les conflits d'imports

#### Service Memory Monitor
Le `ServiceMemoryMonitor` (monitors/service_memory.py) surveille la santé mémoire du service :
- Suivi RSS, utilisation CPU, threads actifs
- Analyse de tendance mémoire avec croissance horaire
- Détection de fuites mémoire
- Garbage collection forcé avec rapport

#### Système de Formatage Complet
Le module `formatters.py` fournit :
- **DataFormatter** : Formatage général (octets, pourcentages, durées)
- **TableFormatter** : Création de tables ASCII
- **ProgressBarFormatter** : Barres de progression personnalisées
- **AlertFormatter** : Formatage d'alertes avec emojis
- **SystemSummaryFormatter** : Résumés système complets
- **JSONFormatter** : Formatage pour API JSON

#### Serveur WebSocket Standalone
Le `StandaloneWebSocketServer` (script principal) :
- Serveur WebSocket indépendant du service de monitoring
- Gestion intégrée des connexions et commandes
- Limite configurable de clients
- Statistiques de connexion en temps réel

### Performances et Optimisations

#### Collecte Parallèle
```python
# Le système utilise ThreadPoolExecutor pour la collecte parallèle
from concurrent.futures import ThreadPoolExecutor

# Configuration du nombre de workers
service = RealtimeMonitoringService(
    max_workers=8  # Paramètre direct, pas dans config
)
```

#### Limites Automatiques

Le système implémente des limites automatiques pour éviter les overflows :

```python
# Limites intégrées (réinitialisation automatique)
- handled_count: Modulo 10,000,000
- error_count: Modulo 1,000,000  
- alerts_count: Maximum 10,000,000
- errors_count: Maximum 1,000,000
- Historique: 1000 snapshots max, TTL 1 heure
```

#### Optimisations WebSocket

```python
# Broadcast avec semaphore
- Limite: 50 envois concurrents
- Timeout: 1 seconde par envoi
- Gestion automatique des clients déconnectés
- Thread naming: "monitoring-broadcast"
```

#### Timeouts et Fallbacks

```python
# Timeouts configurés
- nvidia-smi: 5 secondes
- Mesure CPU: Non-bloquante
- WebSocket send: 1 seconde

# Stratégies de fallback GPU
1. GPUtil (prioritaire)
2. pynvml/nvidia-ml-py3
3. nvidia-smi XML parsing
4. Aucun GPU (dégradation gracieuse)
```

### Débogage et Logging

#### Configuration du Logging

```python
import logging
import sys

# Configuration détaillée du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Activer le debug pour des modules spécifiques
logging.getLogger('monitors.gpu').setLevel(logging.DEBUG)
logging.getLogger('services.websocket_server').setLevel(logging.DEBUG)
```

#### Mode Debug du Service

```python
service = RealtimeMonitoringService(
    debug=True,  # Active les logs détaillés
    config={
        'logging': {
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
)

# Informations de debug disponibles
debug_info = service.get_debug_info()
print(f"Threads actifs: {debug_info['active_threads']}")
print(f"Queue size: {debug_info['queue_size']}")
print(f"Erreurs récentes: {debug_info['recent_errors']}")
```

