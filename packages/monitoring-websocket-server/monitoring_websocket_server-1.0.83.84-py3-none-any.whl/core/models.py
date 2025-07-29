"""Data models for the monitoring system.

This module defines data structures used to represent system information,
including memory, processor, disk, and operating system details, as well as
alerts and monitoring snapshots.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Any

from .enums import AlertLevel


@dataclass
class MemoryInfo:
    """Represent memory information for the system.

    This class encapsulates memory-related metrics including total, available,
    and used memory.

    Attributes:
        total: Total memory in bytes.
        available: Available memory in bytes.
        used: Used memory in bytes.
        percentage: Memory usage as a percentage (0-100).
        timestamp: Unix timestamp when the measurement was taken.
    """
    total: int
    available: int
    used: int
    percentage: float
    timestamp: float


@dataclass
class ProcessorInfo:
    """Represent processor information for the system.

    This class encapsulates CPU-related metrics including usage, core counts,
    and frequency information.

    Attributes:
        usage_percent: Overall CPU usage as a percentage (0-100).
        core_count: Number of physical CPU cores.
        logical_count: Number of logical CPU cores (including hyperthreading).
        frequency_current: Current CPU frequency in MHz.
        frequency_max: Maximum CPU frequency in MHz.
        per_core_usage: List of usage percentages for each CPU core.
        timestamp: Unix timestamp when the measurement was taken.
    """
    usage_percent: float
    core_count: int
    logical_count: int
    frequency_current: float
    frequency_max: float
    per_core_usage: List[float]
    timestamp: float


@dataclass
class DiskInfo:
    """Represent disk information for the system.

    This class encapsulates disk storage metrics for a specific path.

    Attributes:
        total: Total disk space in bytes.
        used: Used disk space in bytes.
        free: Free disk space in bytes.
        percentage: Disk usage as a percentage (0-100).
        path: Filesystem path being monitored.
        timestamp: Unix timestamp when the measurement was taken.
    """
    total: int
    used: int
    free: int
    percentage: float
    path: str
    timestamp: float


@dataclass
class OSInfo:
    """Represent operating system information.

    This class encapsulates detailed information about the operating system
    and system environment.

    Attributes:
        name: Operating system name (e.g., 'Linux', 'Windows').
        version: OS version string.
        release: OS release identifier.
        architecture: System architecture (e.g., 'x86_64').
        machine: Machine type.
        processor: Processor identifier string.
        platform: Platform description.
        python_version: Python interpreter version.
        hostname: System hostname.
        timestamp: Unix timestamp when the information was collected.
    """
    name: str
    version: str
    release: str
    architecture: str
    machine: str
    processor: str
    platform: str
    python_version: str
    hostname: str
    timestamp: float


@dataclass
class Alert:
    """Represent a monitoring alert.

    This class encapsulates information about alerts generated when system
    metrics exceed defined thresholds.

    Attributes:
        timestamp: Date and time when the alert was generated.
        component: System component that triggered the alert (e.g., 'memory', 'cpu').
        metric: Specific metric that exceeded threshold (e.g., 'usage_percent').
        value: Actual value of the metric when alert was triggered.
        threshold: Threshold value that was exceeded.
        level: Severity level of the alert (AlertLevel enum).
        message: Human-readable alert message.
    """
    timestamp: datetime
    component: str
    metric: str
    value: float
    threshold: float
    level: AlertLevel
    message: str


@dataclass
class MonitoringSnapshot:
    """Represent a complete system snapshot at a specific point in time.

    This class aggregates all monitoring data collected at a single moment,
    providing a comprehensive view of system state.

    Attributes:
        timestamp: Date and time when the snapshot was taken.
        memory_info: Memory usage information.
        processor_info: CPU usage and specifications.
        disk_info: Disk usage information.
        os_info: Operating system information.
        gpu_info: Optional GPU information (if available).
        alerts: Optional list of alerts generated for this snapshot.
    """
    timestamp: datetime
    memory_info: MemoryInfo
    processor_info: ProcessorInfo
    disk_info: DiskInfo
    os_info: OSInfo
    gpu_info: Optional[Any] = None  # GPUInfo from monitors.gpu
    alerts: Optional[List[Alert]] = None
