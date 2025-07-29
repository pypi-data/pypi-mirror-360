# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a real-time system monitoring application that collects system metrics (CPU, memory, disk, GPU) and broadcasts them via WebSocket to connected clients. The system is built in Python with a modular architecture.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the WebSocket monitoring server
monitoring-websocket-server

# Run with custom host and port
monitoring-websocket-server --host 127.0.0.1 --port 8080

# Available CLI options:
# --host: WebSocket server host (default: 0.0.0.0)
# --port: WebSocket server port (default: 8765)

# No test client or GPU test scripts available
```

## Architecture

### Component Structure
- **`core/`**: Data models (`MonitoringSnapshot`, `ProcessorInfo`, `MemoryInfo`, etc.) and enums
- **`monitors/`**: System metric collectors (CPU, memory, disk, GPU) - all inherit from `BaseMonitor`
  - Contains CPU frequency detection functions in `processor.py`
- **`services/`**: Core services including `RealtimeMonitoringService` and `WebSocketMonitoringServer`
- **`exporters/`**: Data export mechanisms (JSON file, WebSocket broadcasting)
- **`alerts/`**: Alert system with configurable thresholds and cooldown periods
- **`utils/`**: Helper utilities for display, formatting and system functions

### Key Integration Points

1. **Monitoring Flow**: `SystemMonitor` → `RealtimeMonitoringService` → `MonitoringSnapshot` → Exporters
2. **WebSocket Broadcasting**: `RealtimeMonitoringService` → `WebSocketExporter` → `WebSocketMonitoringServer` → Clients
3. **Standalone Mode**: `monitoring-websocket-server` provides `StandaloneWebSocketServer` that combines monitoring and WebSocket in one

### Development Patterns

- **Async/Sync Hybrid**: Services use asyncio, monitors use ThreadPoolExecutor for concurrent collection
- **Factory Pattern**: Used in `monitors/__init__.py` and `exporters/__init__.py` for dynamic component creation
- **Type Annotations**: Throughout the codebase (Python 3.5+ style)
- **Error Handling**: Custom exceptions (`ServiceStartupError`, `DataCollectionError`) with graceful degradation

### Configuration System

Configuration is centralized in `config.py` using constants:
- Memory thresholds: 80% warning, 90% critical
- Disk thresholds: 85% warning, 95% critical  
- WebSocket server defaults: `ws://0.0.0.0:8765`
- Monitoring interval: 0.5 seconds
- Export interval: 60 seconds
- All values are organized by category with PEP 257 documentation

### Performance Considerations

- Non-blocking CPU measurements to avoid delays
- Concurrent data collection via ThreadPoolExecutor
- Semaphore-limited WebSocket broadcasting (50 concurrent sends)
- Automatic history cleanup (1000 snapshots max, 1-hour TTL)

## Development Notes

- GPU monitoring is optional and auto-detects available libraries (GPUtil, nvidia-ml-py3, nvidia-smi)
- WebSocket messages follow a consistent JSON structure with ISO timestamps
- The system maintains thread safety when using `ThreadSafeMonitoringService`
- Alert cooldown periods prevent spam (default 300 seconds)
- CPU frequency detection functions are located in `monitors/processor.py` with OS-specific implementations
- `monitoring-websocket-server` contains simplified versions of CPU frequency functions (mainly using psutil) to avoid import conflicts
- The root directory should NOT contain an `__init__.py` file to avoid import conflicts