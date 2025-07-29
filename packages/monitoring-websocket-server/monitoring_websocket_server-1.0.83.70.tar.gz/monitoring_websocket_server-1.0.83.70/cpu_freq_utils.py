"""
Utilitaires pour la détection de fréquence CPU.
Ce module est une façade pour les fonctions de détection de fréquence CPU
qui évite les problèmes d'imports relatifs.
"""

import sys
import os
import platform
import subprocess
import re

# Importer psutil directement
try:
    import psutil
except ImportError:
    psutil = None


def get_cpu_current_frequency() -> float:
    """
    Récupère la fréquence actuelle du CPU en MHz.
    
    Essaie plusieurs méthodes dans l'ordre:
    1. psutil (si disponible et fiable)
    2. Méthodes spécifiques au système d'exploitation
    
    Returns:
        Fréquence actuelle en MHz, ou 0 si impossible à déterminer
    """
    # Essayer psutil d'abord
    freq = _get_current_freq_from_psutil()
    if freq and freq > 0:
        return freq
    
    # Essayer les méthodes spécifiques à l'OS
    system = platform.system()
    
    if system == "Windows":
        freq = _get_current_freq_windows()
        if freq:
            return freq
    elif system == "Linux":
        freq = _get_current_freq_linux()
        if freq:
            return freq
    elif system == "Darwin":  # macOS
        freq = _get_current_freq_macos()
        if freq:
            return freq
    
    return 0.0


def _get_current_freq_from_psutil():
    """Récupère la fréquence actuelle via psutil si disponible."""
    if not psutil:
        return None
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.current > 0:
            return cpu_freq.current
    except (AttributeError, Exception):
        pass
    return None


def _get_current_freq_windows():
    """Récupère la fréquence actuelle sur Windows."""
    try:
        ps_cmd = "(Get-CimInstance Win32_Processor).CurrentClockSpeed"
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            freq = float(result.stdout.strip())
            if freq > 0:
                return freq
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    return None


def _get_current_freq_linux():
    """Récupère la fréquence actuelle sur Linux."""
    try:
        cpu_cur_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
        if os.path.exists(cpu_cur_freq_path):
            with open(cpu_cur_freq_path, 'r') as f:
                khz = int(f.read().strip())
                return khz / 1000.0  # Convertir KHz en MHz
    except (OSError, IOError):
        pass
    
    try:
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            cpu_mhz_values = []
            for line in content.split('\n'):
                if line.startswith('cpu MHz'):
                    try:
                        mhz = float(line.split(':')[1].strip())
                        cpu_mhz_values.append(mhz)
                    except (IndexError, ValueError):
                        pass
            if cpu_mhz_values:
                return sum(cpu_mhz_values) / len(cpu_mhz_values)
    except (OSError, IOError):
        pass
    
    return None


def _get_current_freq_macos():
    """Récupère la fréquence actuelle sur macOS."""
    try:
        result = subprocess.run(
            ['sysctl', '-n', 'hw.cpufrequency'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            hz = int(result.stdout.strip())
            return hz / 1_000_000.0  # Convertir Hz en MHz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    return None


def get_cpu_max_frequency() -> float:
    """
    Récupère la fréquence maximale du CPU en MHz.
    
    Essaie plusieurs méthodes dans l'ordre:
    1. psutil (si disponible et fiable)
    2. Méthodes spécifiques au système d'exploitation
    3. Extraction depuis le nom du processeur
    
    Returns:
        Fréquence maximale en MHz, ou 0 si impossible à déterminer
    """
    # Essayer psutil d'abord
    freq = _get_freq_from_psutil()
    if freq and freq != 2500:  # 2500 est souvent une valeur par défaut incorrecte
        return freq
    
    # Essayer les méthodes spécifiques à l'OS
    system = platform.system()
    
    if system == "Windows":
        freq = _get_freq_windows()
        if freq:
            return freq
    elif system == "Linux":
        freq = _get_freq_linux()
        if freq:
            return freq
    elif system == "Darwin":  # macOS
        freq = _get_freq_macos()
        if freq:
            return freq
    
    # En dernier recours, essayer d'extraire du nom du processeur
    freq = _get_freq_from_processor_name()
    if freq:
        return freq
    
    return 0.0


def _get_freq_from_psutil():
    """Récupère la fréquence via psutil si disponible."""
    if not psutil:
        return None
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.max > 0:
            return cpu_freq.max
    except (AttributeError, Exception):
        pass
    return None


def _get_freq_windows():
    """Récupère la fréquence maximale sur Windows via WMI."""
    try:
        ps_command = r"""
        $cpu = Get-CimInstance -ClassName Win32_Processor
        $maxSpeed = $cpu.MaxClockSpeed
        if ($maxSpeed) { 
            Write-Output $maxSpeed 
        } else {
            # Essayer d'extraire depuis le nom
            $name = $cpu.Name
            if ($name -match '(\d+\.?\d*)\s*GHz') {
                $ghz = [double]$matches[1]
                Write-Output ([int]($ghz * 1000))
            } elseif ($name -match '(\d+)\s*MHz') {
                Write-Output $matches[1]
            }
        }
        """
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            mhz = float(result.stdout.strip())
            if mhz > 0 and mhz != 2500:  # Ignorer la valeur par défaut
                return mhz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    return None


def _get_freq_linux():
    """Récupère la fréquence maximale sur Linux."""
    try:
        cpu_max_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
        if os.path.exists(cpu_max_freq_path):
            with open(cpu_max_freq_path, 'r') as f:
                khz = int(f.read().strip())
                return khz / 1000.0  # Convertir KHz en MHz
    except (OSError, IOError):
        pass
    
    try:
        result = subprocess.run(['lscpu'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'CPU max MHz:' in line:
                    mhz = float(line.split(':')[1].strip())
                    return mhz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_freq_macos():
    """Récupère la fréquence maximale sur macOS."""
    try:
        result = subprocess.run(
            ['sysctl', '-n', 'hw.cpufrequency_max'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            hz = int(result.stdout.strip())
            return hz / 1_000_000.0  # Convertir Hz en MHz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    try:
        result = subprocess.run(
            ['sysctl', '-n', 'hw.cpufrequency'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            hz = int(result.stdout.strip())
            return hz / 1_000_000.0
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_freq_from_processor_name():
    """Extrait la fréquence du nom du processeur."""
    try:
        processor_name = platform.processor()
        if not processor_name:
            return None
        
        # Patterns pour extraire la fréquence
        patterns = [
            r'@\s*(\d+\.?\d*)\s*GHz',  # @ 3.70GHz
            r'(\d+\.?\d*)\s*GHz',       # 3.70GHz n'importe où
            r'@\s*(\d+)\s*MHz',         # @ 3700MHz
            r'(\d+)\s*MHz'              # 3700MHz n'importe où
        ]
        
        for pattern in patterns:
            match = re.search(pattern, processor_name, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                # Si c'est en GHz, convertir en MHz
                if 'ghz' in pattern.lower():
                    return value * 1000.0
                else:
                    return value
    except (AttributeError, ValueError):
        pass
    
    return None