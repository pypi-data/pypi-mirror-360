# Real-Time WebSocket Monitoring System

A comprehensive system resource monitoring solution with real-time broadcasting via WebSocket. Collects CPU, memory, disk, and GPU metrics with a configurable alert system.

## Table of Contents

- [1. Installation](#1-installation)
- [2. Quick Start](#2-quick-start)
- [3. Features](#3-features)
- [4. Configuration](#4-configuration)
- [5. WebSocket API](#5-websocket-api)
- [6. Collected Metrics](#6-collected-metrics)
- [7. Alert System](#7-alert-system)
- [8. Advanced Usage](#8-advanced-usage)
- [9. Integration](#9-integration)
- [10. Architecture](#10-architecture)

## 1. Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) NVIDIA drivers for GPU monitoring

### Installation via pip

```bash
pip install monitoring-websocket-server
```

### Installation from source

```bash
# Clone the repository
git clone https://github.com/your-repo/monitoring-websocket-system-server.git
cd monitoring-websocket-system-server

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

**Required:**
- `psutil`: System metrics collection
- `websockets`: WebSocket server
- `colorama`: Colored console output

**Optional (for GPU monitoring):**
- `GPUtil`: Simplified interface for NVIDIA GPUs
- `nvidia-ml-py3` or `pynvml`: Direct access to NVIDIA API

## 2. Quick Start

### 1. Start the monitoring server

```bash
# Server with default configuration
monitoring-websocket-server

# Server with CLI options
monitoring-websocket-server --host 127.0.0.1 --port 8080
```

The server starts on `ws://0.0.0.0:8765` by default. These values can be modified in `config.py`.

### 2. Connect to the server

Once the server is running, you can connect via WebSocket at `ws://localhost:8765`.

See the [WebSocket API](#5-websocket-api) section for JavaScript and Python client examples.

## 3. Features

### Real-Time Metrics Collection

- **CPU/Processor**
  - Global and per-core usage
  - Current and maximum frequency
  - Physical and logical core count
  
- **RAM Memory**
  - Total, available, and used memory
  - Usage percentage
  
- **Disk**
  - Total, used, and free space
  - Usage percentage
  - Monitoring of specific paths
  
- **GPU** (if available)
  - Driver name and version
  - Multi-GPU support with auto-detection
  - Multiple backends: GPUtil → pynvml → nvidia-smi (fallback)
  - Utility methods: `get_gpu_count()`, `is_gpu_available()`
  - GPU and memory usage
  - Temperature and power consumption
  - Multi-GPU support

- **System Information**
  - OS, version, architecture
  - Hostname and process count
  - System boot time

- **Real-Time Alerts**
  - Automatic generation when thresholds are exceeded
  - Two levels: WARNING and CRITICAL
  - Default thresholds:
    - Memory: WARNING at 80%, CRITICAL at 90%
    - Disk: WARNING at 85%, CRITICAL at 95%
  - Instant broadcasting via WebSocket
  - Detailed structure with timestamp, component, value, and message

### WebSocket Broadcasting

- High-performance WebSocket server
- Support for up to 1000 simultaneous clients
- Structured JSON messages with timestamps
- Automatic client-side reconnection
- Optimized broadcast with rate limiting
- **Alerts integrated into monitoring messages**

### Alert System

- Configurable threshold alerts
- WARNING and CRITICAL levels
- Cooldown to prevent spam
- Multiple handlers (console, file, email)
- Customizable callbacks

### Data Export

- JSON export with automatic rotation
- Optional compression
- File timestamping
- Flexible directory configuration

## 4. Configuration

### Configuration System

System configuration is centralized in the `config.py` file which contains all constants used in the project. Values are organized by category for easy maintenance.

#### Modifying Configuration

To modify the configuration, directly edit the constants in the `config.py` file:

```python
# Example of modifying config.py
from config import *

# Change monitoring interval
MONITOR_INTERVAL = 1.0  # Change from 0.5 to 1 second

# Modify memory alert thresholds
MEMORY_WARNING_THRESHOLD = 75.0  # Instead of 80%
MEMORY_CRITICAL_THRESHOLD = 85.0  # Instead of 90%
```

#### Configuration Categories

**WebSocket Network Configuration**
```python
WEBSOCKET_HOST = "0.0.0.0"          # Listening interface
WEBSOCKET_PORT = 8765               # Server port
WEBSOCKET_MAX_CLIENTS = 1000        # Max simultaneous clients
WEBSOCKET_SEND_TIMEOUT = 1.0        # Send timeout (seconds)
```

**Time Intervals**
```python
MONITOR_INTERVAL = 0.5              # Metrics collection (seconds)
EXPORT_INTERVAL = 60.0              # JSON export (seconds)
CLEANUP_INTERVAL = 60.0             # Periodic cleanup (seconds)
ALERT_COOLDOWN = 300.0              # Between identical alerts (seconds)
```

**Alert Thresholds**
```python
# RAM Memory
MEMORY_WARNING_THRESHOLD = 80.0     # Warning threshold (%)
MEMORY_CRITICAL_THRESHOLD = 90.0    # Critical threshold (%)

# Disk
DISK_WARNING_THRESHOLD = 85.0       # Warning threshold (%)
DISK_CRITICAL_THRESHOLD = 95.0      # Critical threshold (%)
DISK_MIN_FREE_GB = 1.0             # Minimum free space (GB)

```

**Limits and Sizes**
```python
MAX_SNAPSHOTS_HISTORY = 1000        # Snapshots in memory
THREAD_POOL_WORKERS = 4             # ThreadPool workers
DATA_QUEUE_SIZE = 100               # Thread-safe queue size
WEBSOCKET_BROADCAST_SEMAPHORE_LIMIT = 50  # Concurrent sends
```

### Usage in Code

Services and components automatically use these constants:

```python
from services.realtime import RealtimeMonitoringService

# The service uses config.py constants by default
service = RealtimeMonitoringService()

# Or override with specific values
service = RealtimeMonitoringService(
    monitor_interval=1.0,  # Override MONITOR_INTERVAL
    export_interval=30.0   # Override EXPORT_INTERVAL
)
```

### Main Default Values

| Category | Constant | Value | Description |
|----------|----------|-------|-------------|
| **WebSocket** | `WEBSOCKET_PORT` | 8765 | Server port |
| **Monitoring** | `MONITOR_INTERVAL` | 0.5s | Collection frequency |
| **Export** | `EXPORT_INTERVAL` | 60s | JSON export frequency |
| **History** | `MAX_SNAPSHOTS_HISTORY` | 1000 | Max snapshots |
| **Alerts** | `ALERT_COOLDOWN` | 300s | Delay between alerts |
| **Memory** | `MEMORY_WARNING_THRESHOLD` | 80% | RAM warning threshold |
| **Disk** | `DISK_WARNING_THRESHOLD` | 85% | Disk warning threshold |

### Complete Documentation

The `config.py` file is fully documented with:
- PEP 257 docstrings for each constant
- Clearly identified section organization
- Explanatory comments for critical values
- Default values optimized for performance

Consult `config.py` directly to see all available options and their detailed documentation.

## 5. WebSocket API

### Connecting to the Server

```javascript
// JavaScript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    console.log('Connected to monitoring server');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Data received:', data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

```python
# Python with websockets
import asyncio
import websockets
import json

async def client():
    async with websockets.connect('ws://localhost:8765') as websocket:
        while True:
            data = await websocket.recv()
            message = json.loads(data)
            print(f"Received: {message}")

asyncio.run(client())
```

### Message Format

#### Alerts in WebSocket Messages

Alerts are automatically included in monitoring messages when configured thresholds are exceeded. The `alerts` field is an optional array that contains:

- **timestamp**: Alert timestamp in ISO 8601 format
- **component**: Affected component (`memory` or `disk`)
- **metric**: Metric that triggered the alert (`usage_percent`)
- **value**: Current metric value
- **threshold**: Threshold that was exceeded
- **level**: Alert level (`WARNING` or `CRITICAL`)
- **message**: Descriptive alert message

Default thresholds are:
- Memory: WARNING at 80%, CRITICAL at 90%
- Disk: WARNING at 85%, CRITICAL at 95%

#### Monitoring Message

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

#### Control Messages

**Ping/Pong:**
```json
// Client sends
{"type": "ping"}

// Server responds
{"type": "pong", "timestamp": "2025-01-03T10:15:30.123456"}
```

**Server Status:**
```json
// Client sends
{"type": "get_status"}

// Server responds
{
  "type": "status",
  "connected_clients": 5,
  "server_start_time": "2025-01-03T10:00:00.000000",
  "message": "Server is running"
}
```

**Error Messages:**
```json
{
  "type": "error",
  "message": "Invalid message format",
  "code": "INVALID_FORMAT"
}
```

### Client-Side Alert Handling

JavaScript example for processing received alerts:

```javascript
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    if (message.type === 'monitoring_data') {
        // Process monitoring data
        updateMetrics(message.data);
        
        // Check and process alerts
        if (message.alerts && message.alerts.length > 0) {
            message.alerts.forEach(alert => {
                if (alert.level === 'CRITICAL') {
                    console.error(`🚨 CRITICAL: ${alert.message}`);
                    // Display urgent notification
                    showCriticalNotification(alert);
                } else if (alert.level === 'WARNING') {
                    console.warn(`⚠️ WARNING: ${alert.message}`);
                    // Display warning
                    showWarningNotification(alert);
                }
            });
        }
    }
};
```

### Available Commands

| Command | Description | Response | Example |
|---------|-------------|----------|---------|
| `ping` | Connectivity test | `pong` with timestamp | `{"type": "ping"}` |
| `get_status` | Server status | Server information | `{"type": "get_status"}` |
| `subscribe` | Subscribe to updates | Subscription confirmation | `{"type": "subscribe"}` |
| `unsubscribe` | Unsubscribe | Unsubscription confirmation | `{"type": "unsubscribe"}` |

**Complete WebSocket Protocol:**

```python
# Supported control messages
messages = {
    # Client -> Server
    "ping": {"type": "ping"},
    "get_status": {"type": "get_status"},
    "subscribe": {"type": "subscribe"},
    "unsubscribe": {"type": "unsubscribe"},
    
    # Server -> Client
    "connection": {"type": "connection", "status": "connected"},
    "monitoring_data": {"type": "monitoring_data", "data": {...}},
    "pong": {"type": "pong", "timestamp": "..."},
    "status": {"type": "status", "server_version": "...", ...},
    "error": {"type": "error", "message": "...", "code": "..."}
}

# Timeout and limit handling
- WebSocket send: 1 second
- Broadcast: Semaphore limited to 50 concurrent
- Automatic reconnection: Not implemented server-side
- Client limit: 1000 by default (configurable)
```

## 6. Collected Metrics

### Processor (CPU)

| Metric | Description | Unit |
|--------|-------------|------|
| `usage_percent` | Global usage | % |
| `per_core_usage` | Per-core usage | % |
| `core_count` | Physical cores | count |
| `logical_count` | Logical cores | count |
| `frequency_current` | Current frequency | MHz |
| `frequency_max` | Maximum frequency | MHz |

### RAM Memory

| Metric | Description | Unit |
|--------|-------------|------|
| `total` | Total memory | bytes |
| `available` | Available memory | bytes |
| `used` | Used memory | bytes |
| `percentage` | Used percentage | % |

### Disk

| Metric | Description | Unit |
|--------|-------------|------|
| `total` | Total space | bytes |
| `used` | Used space | bytes |
| `free` | Free space | bytes |
| `percentage` | Used percentage | % |
| `path` | Monitored path | string |

### GPU (if available)

| Metric | Description | Unit |
|--------|-------------|------|
| `name` | GPU name | string |
| `driver_version` | Driver version | string |
| `memory_total` | Total memory | bytes |
| `memory_used` | Used memory | bytes |
| `memory_free` | Free memory | bytes |
| `gpu_usage_percent` | GPU usage | % |
| `temperature` | Temperature | °C |
| `power_draw` | Current power draw | W |
| `power_limit` | Power limit | W |

## 7. Alert System

### Threshold Configuration

```python
from services.realtime import RealtimeMonitoringService
from alerts.alert_handlers import ConsoleAlertHandler, FileAlertHandler

# Create monitoring service
service = RealtimeMonitoringService()

# Configure alert thresholds
service.alert_manager.set_threshold('memory', 'warning', 75)
service.alert_manager.set_threshold('memory', 'critical', 85)
service.alert_manager.set_threshold('disk', 'warning', 80)
service.alert_manager.set_threshold('disk', 'critical', 95)
# Note: CPU is not in valid components (only memory and disk)

# Add alert handlers
service.alert_manager.add_handler(ConsoleAlertHandler())
service.alert_manager.add_handler(FileAlertHandler("./alerts.log"))
```

### Alert Types

1. **WARNING**: Warning threshold exceeded
2. **CRITICAL**: Critical threshold exceeded

### Available Alert Handlers

#### ConsoleAlertHandler
Displays alerts in console with colors:
- Yellow for WARNING
- Red for CRITICAL

```python
from alerts.handlers import ConsoleAlertHandler
handler = ConsoleAlertHandler(name="console")
```

#### FileAlertHandler
Logs alerts to a file:

```python
from alerts.handlers import FileAlertHandler
handler = FileAlertHandler(name="file", log_file="./monitoring_alerts.log")
```

#### EmailAlertHandler
Sends alerts via email:

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

#### Advanced FileAlertHandler
Automatic log rotation at 10MB:

```python
from alerts.alert_handlers import FileAlertHandler

# Automatic log file rotation
handler = FileAlertHandler(
    log_file="./monitoring_alerts.log",
    max_file_size=10*1024*1024  # 10MB
)
```

#### WebhookAlertHandler
Sends alerts to an HTTP/HTTPS webhook:

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
Native Slack integration:

```python
from alerts.handlers import SlackAlertHandler

handler = SlackAlertHandler(
    name="slack",
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    channel="#monitoring",  # Optional
    username="MonitoringBot"
)
# Note: Emojis and colors are automatically managed based on alert level
```

### Alert Filters

```python
from alerts.handlers import create_level_filter, create_component_filter, create_time_filter

# Filter by minimum level
from core.enums import AlertLevel
level_filter = create_level_filter(AlertLevel.WARNING)

# Filter by components
component_filter = create_component_filter(
    allowed_components=["memory", "cpu"]
)

# Filter by time range (supports ranges crossing midnight)
time_filter = create_time_filter(
    start_hour=9,
    end_hour=18,
    timezone="Europe/Paris"
)

# Apply filters
handler.add_filter(level_filter)
handler.add_filter(component_filter)
handler.add_filter(time_filter)
```

##### Handler Manager

```python
from alerts.handlers import AlertHandlerManager

# Create centralized manager
manager = AlertHandlerManager()

# Add multiple handlers
console_handler = ConsoleAlertHandler()
file_handler = FileAlertHandler("alerts.log")
slack_handler = SlackAlertHandler(webhook_url="...")

manager.add_handler(console_handler)
manager.add_handler(file_handler)
manager.add_handler(slack_handler)

# Management methods
manager.list_handlers()  # List all handlers
handler = manager.get_handler("file")  # Get specific handler

# Retrieve and manage specific handlers
file_handler = manager.get_handler("file")
if file_handler:
    file_handler.enabled = False  # Disable
    file_handler.enabled = True   # Re-enable

# Remove a handler
manager.remove_handler("file")

# Batch operations
manager.enable_all()
manager.disable_all()
manager.clear_all()

# Distribute an alert
results = manager.handle_alert(alert)
for handler_name, success in results.items():
    print(f"{handler_name}: {'Success' if success else 'Failed'}")

# Get statistics
stats = manager.get_statistics()
print(f"Alerts handled: {stats['total_handled']}")
print(f"Errors: {stats['total_errors']}")
```

### Advanced Handler Methods

```python
# Filter management
handler.add_filter(my_filter)
handler.remove_filter(my_filter)
handler.clear_filters()

# Manual verification
if handler.should_handle(alert):
    handler.handle(alert)

# Access counters (with anti-overflow protection)
print(f"Alerts handled: {handler.handled_count}")
print(f"Errors: {handler.error_count}")
```

### Custom Callbacks

```python
def custom_alert_callback(alert):
    print(f"Custom alert: {alert.level} - {alert.message}")
    # Send to external system, SMS, Slack, etc.

service.alert_manager.add_alert_callback(custom_alert_callback)
```

### Alert Cooldown

To prevent spam, a cooldown system is integrated:
- Default delay: 300 seconds (5 minutes)
- Configurable per alert type

```python
# Modify global cooldown (not per component)
service.alert_manager.cooldown_seconds = 600  # 10 minutes
```

## 8. Advanced Usage

### Advanced Service Methods

```python
from services.realtime import RealtimeMonitoringService

service = RealtimeMonitoringService()
service.start()

# Get formatted system state summary
summary = service.get_system_summary()
print(summary)

# Retrieve history with limit
history = service.get_snapshots_history(count=100)

# Force immediate export (async method)
import asyncio
asyncio.run(service.force_export())

# Dynamically configure thresholds
service.configure_thresholds({
    'memory_warning': 70,
    'memory_critical': 85,
    'disk_warning': 80,
    'disk_critical': 90
})

# Get complete health report
health_report = service.get_health_report()
print(f"Service health: {health_report['service']['status']}")
print(f"Uptime: {health_report['service']['uptime_seconds']}s")
print(f"Statistics: {health_report['statistics']}")
```

### Advanced Configuration Parameters

```python
from services.realtime import RealtimeMonitoringService

# Advanced service configuration (direct parameters)
from pathlib import Path

service = RealtimeMonitoringService(
    monitor_interval=0.5,
    export_interval=60.0,
    max_snapshots_history=1000,
    export_dir=Path("./monitoring_data"),
    max_workers=8  # Number of ThreadPoolExecutor workers
)

# Access service properties
print(f"Status: {service.status}")
print(f"Running: {service.is_running}")
snapshot = service.current_snapshot  # Property, not method

# History access methods
history = service.get_snapshots_history()  # Complete history
recent = service.get_snapshots_history(count=50)  # Last N snapshots
```

### Thread-Safe Mode

For use in multi-threaded applications:

```python
from services.threadsafe import ThreadSafeMonitoringService

# Create thread-safe service with advanced configuration
service = ThreadSafeMonitoringService(
    data_queue_size=100  # Queue size (default: 100)
)
service.start()

# Usage from multiple threads
def worker_thread():
    while True:
        data = service.get_current_data()
        if data:
            print(f"CPU: {data['cpu']['usage_percent']}%")
            print(f"Memory: {data['memory']['usage_percent']}%")
        time.sleep(1)

# Launch multiple threads
threads = []
for i in range(5):
    t = threading.Thread(target=worker_thread)
    t.start()
    threads.append(t)
```

### Custom Export

#### Create a Custom Exporter

```python
from exporters.base import BaseExporter
from typing import Dict, Any

class CustomExporter(BaseExporter):
    def export(self, data: Dict[str, Any]) -> None:
        # Your custom export logic
        print(f"Custom export: {data}")
    
    def initialize(self) -> None:
        print("Initializing custom exporter")
    
    def cleanup(self) -> None:
        print("Cleaning up custom exporter")

# Use custom exporter
# Note: RealtimeMonitoringService uses a single exporter (JSONExporter by default)
# For a custom exporter, you would need to modify the service source code
```

#### Integrated WebSocketExporter

```python
from exporters.websocket_exporter import WebSocketExporter

# Create WebSocket exporter for custom integration
ws_exporter = WebSocketExporter(
    host="0.0.0.0",
    port=8765,
    export_interval=1.0
)

# Available methods
ws_exporter.start_server()  # Start server in separate thread
ws_exporter.stop_server()   # Stop server
info = ws_exporter.get_export_info()  # Get export info

# Note: RealtimeMonitoringService doesn't have a list of exporters
# It uses a single exporter configured at initialization
```

#### Advanced JSONExporter Options

```python
from exporters.json_exporter import JSONExporter
from pathlib import Path

# Advanced JSON export configuration
json_exporter = JSONExporter(
    output_dir=Path("./monitoring_data"),
    compress=True,          # gzip compression
    pretty_print=True,      # Indented JSON
    date_in_filename=True   # Format: monitoring_20250103.json or .json.gz
)
# Note: No export_interval or max_file_size parameter in JSONExporter
```

#### WebSocketExporter Methods

```python
from exporters.websocket_exporter import WebSocketExporter

# WebSocketExporter specific methods
ws_exporter = WebSocketExporter()

# Export single snapshot (async)
await ws_exporter.export_snapshot(snapshot)

# The destructor automatically stops the server
# when the object is deleted (__del__ method)
```

### Selective Monitoring

```python
from monitors import create_system_monitor

# Create monitor with only certain components
monitor = create_system_monitor(
    enable_processor=True,
    enable_memory=True,
    enable_disk=False,  # Disable disk monitoring
    enable_gpu=False    # Disable GPU monitoring
)

# Use the monitor
data = monitor.collect()
print(f"CPU: {data['processor']['usage_percent']}%")
print(f"RAM: {data['memory']['percentage']}%")
```

### Advanced GPU Utilities

```python
from monitors.gpu import GPUMonitor

# Using GPU Monitor
monitor = GPUMonitor()

# Check GPU availability
if monitor.is_available():
    # Collect GPU data
    gpu_data = monitor.collect()
    if gpu_data:
        print(f"Number of GPUs: {gpu_data['count']}")
        for gpu in gpu_data['gpus']:
            print(f"GPU {gpu['id']}: {gpu['name']}")
            print(f"  Memory: {gpu['memory_used']}/{gpu['memory_total']} MB")
            print(f"  Usage: {gpu['gpu_usage_percent']}%")
            print(f"  Temperature: {gpu['temperature']}°C")

# GPU backend detection (priority order)
# 1. GPUtil (simplest)
# 2. pynvml/nvidia-ml-py3 (direct NVML access)
# 3. nvidia-smi XML parsing (fallback)

monitor = GPUMonitor()
info = monitor.get_gpu_info()  # Alias for get_data()
```

### Service Memory Monitoring

```python
from monitors.service_memory import ServiceMemoryMonitor

# Create internal memory monitor
memory_monitor = ServiceMemoryMonitor()

# Get current statistics
stats = memory_monitor.get_current_stats()
print(f"RSS Memory: {stats['rss'] / (1024**2):.1f} MB")
print(f"Usage: {stats['percent']:.1f}%")
print(f"Active threads: {stats['thread_count']}")
print(f"Open files: {stats['open_files']}")
print(f"Connections: {stats['connections']}")
print(f"GC collections: {stats['gc_collections']}")  # (gen0, gen1, gen2)

# Analyze memory trend
trend = memory_monitor.get_memory_trend(minutes=60)  # Last hour
if trend.get('status') == 'ok':
    print(f"Growth: {trend['growth_rate_per_hour'] / (1024**2):.1f} MB/hour")
    print(f"Average memory: {trend['average_memory'] / (1024**2):.1f} MB")

# Check memory health
is_healthy, warnings = memory_monitor.check_memory_health()
if not is_healthy:
    print(f"Memory issues detected:")
    for warning in warnings:
        print(f"  - {warning}")
    
# Force garbage collection
result = memory_monitor.force_garbage_collection()
print(f"Memory freed: {result['memory_freed'] / (1024**2):.1f} MB")
print(f"Objects collected: {result['objects_collected']}")

# Complete summary
summary = memory_monitor.get_summary()
print(summary)
```

### Display Manager

```python
from utils.display import DisplayManager

# Create display manager
display = DisplayManager(
    clear_screen=True,  # Clear screen between updates
    compact_mode=False  # Detailed mode
)

# Check if clear screen is supported
if display.clear_supported:
    display.clear_screen()

# Available display methods
display.print_header("MY CUSTOM MONITORING")  # Header
display.print_separator("-", 80)  # Separator line

# Compact mode (for IDE)
display.print_compact_header(iteration=1, timestamp="2025-01-03 10:15:30")
display.print_compact_metrics(data)  # One line with emojis

# Detailed mode
display.print_detailed_metrics(data)

# Specialized sections  
display.print_alerts_section(alerts, recent_alerts)
display.print_statistics_section(stats)

# Note: DisplayManager doesn't have 'compact_mode' property or 'show_metrics' method
```

### Dynamic Configuration Modification

```python
# config.py constants are used at initialization
# To modify dynamically, pass values to constructors

from services.realtime import RealtimeMonitoringService

# Create service with custom values
service = RealtimeMonitoringService(
    monitor_interval=2.0,      # Instead of MONITOR_INTERVAL
    export_interval=120.0,     # Instead of EXPORT_INTERVAL
    max_snapshots_history=500  # Instead of MAX_SNAPSHOTS_HISTORY
)

# For permanent changes, modify config.py directly
```

### History and Statistics

```python
from services.realtime import RealtimeMonitoringService
import statistics

service = RealtimeMonitoringService()
service.start()

# Wait a few seconds to collect data
time.sleep(30)

# Get history
history = service.get_snapshot_history(limit=60)

# Calculate statistics
cpu_values = [s.processor_info.usage_percent for s in history if s.processor_info]
memory_values = [s.memory_info.percentage for s in history if s.memory_info]

print(f"CPU - Average: {statistics.mean(cpu_values):.2f}%")
print(f"CPU - Max: {max(cpu_values):.2f}%")
print(f"Memory - Average: {statistics.mean(memory_values):.2f}%")
print(f"Memory - Max: {max(memory_values):.2f}%")
```

### Enhanced CPU Frequency Detection

```python
from monitors.processor import get_cpu_max_frequency, get_cpu_current_frequency

# Uses advanced methods adapted to each OS (Windows, Linux, macOS)
max_freq = get_cpu_max_frequency()
current_freq = get_cpu_current_frequency()

print(f"Maximum frequency: {max_freq} MHz")
print(f"Current frequency: {current_freq} MHz")

# Note: The main script contains simplified versions of these functions
# that mainly use psutil to avoid import conflicts
```

## 9. Integration

### Integration with FastAPI

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
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/api/monitoring/current")
async def get_current_metrics():
    snapshot = monitoring_service.current_snapshot
    return snapshot.to_dict() if snapshot else {"error": "No data available"}
```

### Integration with Flask

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
    """Thread to send monitoring data"""
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
    print('Client connected')
    emit('connected', {'data': 'Connected to monitoring server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    monitoring_service.start()
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5000)
```

### Integration with Django

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
                print(f"Error sending data: {e}")

# monitoring/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/monitoring/$', consumers.MonitoringConsumer.as_asgi()),
]
```

### Integration with Prometheus

```python
from prometheus_client import Gauge, start_http_server
from services.realtime import RealtimeMonitoringService
import time

# Create Prometheus metrics
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
            
            # Memory
            if snapshot.memory:
                memory_usage.set(snapshot.memory.percentage)
            
            # Disk
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
        
        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    # Start Prometheus HTTP server on port 8000
    start_http_server(8000)
    print("Prometheus server started on http://localhost:8000")
    update_prometheus_metrics()
```

### Integration with Databases

#### Export to InfluxDB

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
            
        # Create data points
        points = []
        
        # CPU
        if snapshot.processor:
            point = Point("cpu") \
                .field("usage_percent", snapshot.processor.usage_percent) \
                .field("frequency_current", snapshot.processor.frequency_current)
            points.append(point)
        
        # Memory
        if snapshot.memory:
            point = Point("memory") \
                .field("percentage", snapshot.memory.percentage) \
                .field("used", snapshot.memory.used) \
                .field("available", snapshot.memory.available)
            points.append(point)
        
        # Write to InfluxDB
        self.write_api.write(bucket=self.bucket, org=self.org, record=points)
    
    def cleanup(self) -> None:
        self.client.close()

# Usage with custom exporter
# Note: RealtimeMonitoringService uses JSONExporter by default
# To use InfluxDBExporter, you would need to modify the service code
# or create a custom service that uses this exporter

influx_exporter = InfluxDBExporter(
    url="http://localhost:8086",
    token="your-token",
    org="your-org",
    bucket="monitoring"
)
```

#### Export to PostgreSQL/MySQL

```python
import psycopg2  # or pymysql for MySQL
from datetime import datetime

class DatabaseExporter(BaseExporter):
    def __init__(self, connection_params, export_interval=60):
        super().__init__(export_interval)
        self.connection_params = connection_params
        self._init_database()
    
    def _init_database(self):
        # Create tables if they don't exist
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


### Project Structure

```
monitoring-websocket-system-server/
├── core/                       # System core
│   ├── __init__.py
│   ├── models.py              # Data models (snapshots, info, alerts)
│   ├── enums.py               # Enumerations (AlertLevel, etc.)
│   └── exceptions.py          # Custom exceptions
│
├── monitors/                   # Metric collectors
│   ├── __init__.py
│   ├── base.py                # Abstract base class
│   ├── processor.py           # CPU monitoring
│   ├── memory.py              # RAM monitoring
│   ├── disk.py                # Disk monitoring
│   ├── gpu.py                 # GPU monitoring with integrated detection
│   ├── system.py              # Complete system monitor
│   ├── service_memory.py      # Internal service memory monitoring
│   └── factory.py             # Factory for monitor creation
│
├── services/                   # Main services
│   ├── __init__.py
│   ├── realtime.py            # Real-time monitoring service
│   ├── threadsafe.py          # Thread-safe version
│   └── websocket_server.py    # WebSocket server
│
├── exporters/                  # Data export
│   ├── __init__.py
│   ├── base.py                # Abstract base class
│   ├── json_exporter.py       # JSON export with rotation
│   ├── websocket_exporter.py  # WebSocket broadcast export
│   └── factory.py             # Factory for exporter creation
│
├── alerts/                     # Alert system
│   ├── __init__.py
│   ├── manager.py             # Alert manager
│   └── handlers.py            # Handlers (console, file, email, webhook, slack)
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── display.py             # Console display management
│   ├── formatters.py          # Complete formatting (tables, progress bars, etc.)
│   └── system.py              # System utilities
│
├── pypi/                       # PyPI publishing scripts
│   ├── publish_pypi.bat
│   └── publish_pypitest.bat
│
├── config.py                   # Centralized configuration constants
├── run_server.py              # Main WebSocket server script with CLI options
├── requirements.txt           # Python dependencies
├── setup.py                   # Package configuration
├── pyproject.toml             # Modern Python configuration
├── MANIFEST.in                # Package manifest
├── README.md                  # Main documentation
└── CLAUDE.md                  # Instructions for Claude Code
```

### Architecture Diagram

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

### Data Flow

#### 1. **Data Collection Layer** 🔍
- **Individual Monitors**: Each system component has a dedicated monitor
  - CPU Monitor: Tracks usage percentage, frequency, and core counts
  - Memory Monitor: Monitors total, used, and available memory
  - Disk Monitor: Tracks disk space usage and availability
  - GPU Monitor: Monitors GPU usage, memory, and temperature (if available)
  
- **System Monitor Aggregation**: Combines all monitor data into unified snapshots
  - Parallel collection using ThreadPoolExecutor (4 workers by default)
  - Non-blocking operations to prevent delays
  - Automatic error handling and graceful degradation

#### 2. **Processing & Analysis Layer** 🔧
- **Realtime Service**: Central orchestrator for data processing
  - Maintains history of last 1000 snapshots
  - Automatic cleanup of old data (1-hour TTL)
  - Thread-safe operations with "monitoring-" prefix naming
  - Export scheduling at configurable intervals

- **Alert Manager**: Real-time threshold monitoring
  - Configurable thresholds for each metric
  - Alert generation with WARNING and CRITICAL levels
  - 5-minute cooldown to prevent spam
  - Dispatches alerts to multiple handlers simultaneously

- **Alert Handlers**: Specialized alert processing
  - Console: Color-coded output (Yellow/Red)
  - File: Log rotation at 10MB
  - Email: SMTP with TLS support
  - Webhook: HTTP/HTTPS endpoints
  - Slack: Native integration with emojis

#### 3. **Data Distribution Layer** 📤
- **JSON Exporter**: Persistent data storage
  - Automatic file rotation with timestamps
  - Optional gzip compression
  - Pretty-print formatting available
  - Date-based file naming (monitoring_YYYYMMDD.json)

- **WebSocket Server**: Real-time data streaming
  - Listens on port 8765 by default
  - Supports up to 1000 concurrent clients
  - Broadcast rate limited to 50 messages/second
  - Semaphore-based concurrency control
  - Control command support (ping/pong, status, subscribe)

#### 4. **Client Consumption** 📊
- **WebSocket Clients**: Real-time data consumers
  - Receive structured JSON messages
  - Integrated alert notifications
  - Control message support
  - Automatic reconnection handling (client-side)
  - Multi-platform support (JavaScript, Python, etc.)

### Design Patterns

- **Factory Pattern**: Dynamic creation of monitors and exporters (monitors/factory.py, exporters/factory.py)
- **Observer Pattern**: Alert system with callbacks
- **Module Pattern**: Centralized configuration via constants (config.py)
- **Strategy Pattern**: Different export strategies (JSON, WebSocket)
- **Template Method**: Abstract base classes (base.py in monitors and exporters)
- **Handler Pattern**: Modular alert management (ConsoleHandler, FileHandler, EmailHandler, WebhookHandler, SlackHandler)

### Key Architecture Components

#### Monitors (Data Collection)
Each monitor inherits from `BaseMonitor` and implements the `collect()` method:

```python
monitors/
├── base.py          # Abstract base class defining the monitor interface
├── processor.py     # CPU monitoring with frequency detection
├── memory.py        # RAM monitoring
├── disk.py          # Disk space monitoring
├── gpu.py           # GPU monitoring with multi-backend support
└── system.py        # Aggregates all monitors into a unified collector
```

#### Services (Core Logic)
The service layer orchestrates monitoring and data distribution:

```python
services/
├── realtime.py      # Main monitoring service with history and export scheduling
├── threadsafe.py    # Thread-safe wrapper for multi-threaded applications
└── websocket_server.py  # WebSocket server for real-time broadcasting
```

#### Exporters (Data Output)
Exporters handle different output formats and destinations:

```python
exporters/
├── base.py          # Abstract base class for exporters
├── json_exporter.py # File-based JSON export with rotation
└── websocket_exporter.py  # Real-time WebSocket broadcasting
```

#### Alerts (Notification System)
Comprehensive alert system with multiple notification channels:

```python
alerts/
├── manager.py       # Alert threshold management and dispatching
└── handlers.py      # Various notification handlers (Console, File, Email, etc.)
```

### New Components

#### CPU Frequency Detection
CPU frequency detection functions are integrated in `monitors/processor.py`:
- `get_cpu_max_frequency()`: Detects maximum CPU frequency
- `get_cpu_current_frequency()`: Detects current CPU frequency
- Specific implementations for Windows, Linux, and macOS
- Automatic fallback on multiple detection methods
- Management of incorrect values returned by psutil
- The main script contains simplified versions of these functions to avoid import conflicts

#### Service Memory Monitor
The `ServiceMemoryMonitor` (monitors/service_memory.py) monitors service memory health:
- RSS tracking, CPU usage, active threads
- Memory trend analysis with hourly growth
- Memory leak detection
- Forced garbage collection with report

#### Complete Formatting System
The `formatters.py` module provides:
- **DataFormatter**: General formatting (bytes, percentages, durations)
- **TableFormatter**: ASCII table creation
- **ProgressBarFormatter**: Custom progress bars
- **AlertFormatter**: Alert formatting with emojis
- **SystemSummaryFormatter**: Complete system summaries
- **JSONFormatter**: Formatting for JSON API

#### Standalone WebSocket Server
The `StandaloneWebSocketServer` (main script):
- WebSocket server independent of monitoring service
- Integrated connection and command management
- Configurable client limit
- Real-time connection statistics

### Performance and Optimizations

#### Parallel Collection
```python
# The system uses ThreadPoolExecutor for parallel collection
from concurrent.futures import ThreadPoolExecutor

# Configure number of workers
service = RealtimeMonitoringService(
    max_workers=8  # Direct parameter, not in config
)
```

#### Automatic Limits

The system implements automatic limits to prevent overflows:

```python
# Built-in limits (automatic reset)
- handled_count: Modulo 10,000,000
- error_count: Modulo 1,000,000  
- alerts_count: Maximum 10,000,000
- errors_count: Maximum 1,000,000
- History: 1000 snapshots max, 1-hour TTL
```

#### WebSocket Optimizations

```python
# Broadcast with semaphore
- Limit: 50 concurrent sends
- Timeout: 1 second per send
- Automatic disconnected client management
- Thread naming: "monitoring-broadcast"
```

#### Timeouts and Fallbacks

```python
# Configured timeouts
- nvidia-smi: 5 seconds
- CPU measurement: Non-blocking
- WebSocket send: 1 second

# GPU fallback strategies
1. GPUtil (priority)
2. pynvml/nvidia-ml-py3
3. nvidia-smi XML parsing
4. No GPU (graceful degradation)
```

### Debugging and Logging

#### Logging Configuration

```python
import logging
import sys

# Detailed logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Enable debug for specific modules
logging.getLogger('monitors.gpu').setLevel(logging.DEBUG)
logging.getLogger('services.websocket_server').setLevel(logging.DEBUG)
```

#### Service Debug Mode

```python
service = RealtimeMonitoringService(
    debug=True,  # Enable detailed logs
    config={
        'logging': {
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
)

# Available debug information
debug_info = service.get_debug_info()
print(f"Active threads: {debug_info['active_threads']}")
print(f"Queue size: {debug_info['queue_size']}")
print(f"Recent errors: {debug_info['recent_errors']}")
```