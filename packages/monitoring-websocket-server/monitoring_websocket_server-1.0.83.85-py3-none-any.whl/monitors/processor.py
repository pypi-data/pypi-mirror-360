"""
Moniteur de processeur système.
Surveillance de l'utilisation du CPU et de ses caractéristiques.
"""

import logging
import time
import platform
import subprocess
import re
import os
from typing import Optional, List, Tuple, Dict, Any

import psutil

from ..config import (
    PROCESSOR_CHECK_INTERVAL, PROCESSOR_FALLBACK_INTERVAL
)
from .base import BaseMonitor
from ..core.models import ProcessorInfo
from ..core.exceptions import InvalidIntervalError



class ProcessorMonitor(BaseMonitor):
    """Moniteur pour surveiller l'utilisation du processeur."""

    def __init__(self, interval: float = PROCESSOR_CHECK_INTERVAL) -> None:
        """Initialiser le moniteur de processeur.

        Args:
            interval: Intervalle de mesure en secondes.
        """
        super().__init__("Processor")
        self._interval: float = self._validate_interval(interval)
        self._last_check: Optional[ProcessorInfo] = None
        self._logger = logging.getLogger(__name__)
        
        # Variables pour la mesure non-bloquante du CPU
        self._last_cpu_times: Optional[Any] = None
        self._last_cpu_check_time: Optional[float] = None
        self._last_per_cpu_times: Optional[List[Any]] = None
        
        # Liste des attributs CPU pour éviter l'utilisation de dir()
        self._cpu_time_attrs: List[str] = ['user', 'nice', 'system', 'idle', 'iowait', 
                                            'irq', 'softirq', 'steal', 'guest', 'guest_nice']

    @property
    def interval(self) -> float:
        """Retourner l'intervalle de mesure.

        Returns:
            Intervalle en secondes.
        """
        return self._interval

    @interval.setter
    def interval(self, new_interval: float) -> None:
        """Définir l'intervalle de mesure.

        Args:
            new_interval: Nouvel intervalle en secondes.

        Raises:
            InvalidIntervalError: Si l'intervalle est invalide.
        """
        self._interval = self._validate_interval(new_interval)

    @property
    def last_check(self) -> Optional[ProcessorInfo]:
        """Retourner les dernières informations processeur récupérées.

        Returns:
            Dernières informations processeur ou None.
        """
        return self._last_check

    @staticmethod
    def _validate_interval(interval: float) -> float:
        """Valider l'intervalle de mesure.

        Args:
            interval: Intervalle à valider.

        Returns:
            Intervalle validé.

        Raises:
            InvalidIntervalError: Si l'intervalle est invalide.
        """
        if interval <= 0:
            raise InvalidIntervalError("L'intervalle doit être positif")
        if interval > 10.0:
            raise InvalidIntervalError("L'intervalle ne doit pas dépasser 10 secondes")
        return interval

    def _do_initialize(self) -> None:
        """Initialiser le moniteur de processeur.

        Raises:
            Exception: Si psutil n'est pas disponible.
        """
        try:
            # Test des fonctionnalités CPU
            psutil.cpu_count()
            
            # Initialiser la mesure non-bloquante du CPU
            # Premier appel pour initialiser les valeurs de référence
            psutil.cpu_percent(interval=None)
            psutil.cpu_percent(interval=None, percpu=True)
            
            # Stocker les temps CPU initiaux pour le calcul manuel
            self._last_cpu_times = psutil.cpu_times()
            self._last_per_cpu_times = psutil.cpu_times(percpu=True)
            self._last_cpu_check_time = time.time()
            
        except Exception as e:
            raise Exception(f"Impossible d'accéder aux informations processeur: {e}")

    def _collect_data(self) -> ProcessorInfo:
        """Collecter les informations actuelles sur le processeur.

        Returns:
            Informations détaillées sur le processeur.

        Raises:
            Exception: En cas d'erreur de collecte.
        """
        current_time = time.time()

        try:
            # Utilisation CPU non-bloquante
            if self._last_cpu_check_time is None:
                # Première mesure, utiliser psutil sans intervalle
                per_core_usage = psutil.cpu_percent(interval=None, percpu=True)
                cpu_percent = psutil.cpu_percent(interval=None)
                
                # Si les valeurs sont nulles (première mesure), utiliser un fallback rapide
                if cpu_percent == 0:
                    # Utiliser une mesure avec un intervalle très court comme fallback
                    cpu_percent = psutil.cpu_percent(interval=PROCESSOR_FALLBACK_INTERVAL)
                    per_core_usage = psutil.cpu_percent(interval=PROCESSOR_FALLBACK_INTERVAL, percpu=True)
                
                # Initialiser les temps de référence
                self._last_cpu_times = psutil.cpu_times()
                self._last_per_cpu_times = psutil.cpu_times(percpu=True)
                self._last_cpu_check_time = current_time
            else:
                # Utiliser psutil sans intervalle (non-bloquant)
                cpu_percent = psutil.cpu_percent(interval=None)
                per_core_usage = psutil.cpu_percent(interval=None, percpu=True)
                
                # Si psutil retourne 0 (pas assez de temps écoulé), calculer manuellement
                if cpu_percent == 0 or not per_core_usage or all(v == 0 for v in per_core_usage):
                    per_core_usage = self._calculate_cpu_percent_manual(percpu=True)
                    cpu_percent = self._calculate_cpu_percent_manual(percpu=False)
                
                # Mettre à jour les temps de référence
                self._last_cpu_times = psutil.cpu_times()
                self._last_per_cpu_times = psutil.cpu_times(percpu=True)
                self._last_cpu_check_time = current_time

            # Information CPU
            core_count = psutil.cpu_count(logical=False) or 0
            logical_count = psutil.cpu_count(logical=True) or 0

            # Fréquences CPU
            try:
                freq_info = psutil.cpu_freq()
                freq_current = freq_info.current if freq_info else 0.0
                freq_max = freq_info.max if freq_info else 0.0
                
                # Utiliser notre fonction améliorée pour la fréquence max si nécessaire
                if get_cpu_max_frequency and (freq_max == 2500 or freq_max == 0 or freq_max is None):
                    better_freq = get_cpu_max_frequency()
                    if better_freq > 0:
                        freq_max = better_freq
                
                # Utiliser notre fonction améliorée pour la fréquence actuelle si nécessaire
                if get_cpu_current_frequency and (freq_current == 0 or freq_current is None):
                    better_current = get_cpu_current_frequency()
                    if better_current > 0:
                        freq_current = better_current
                        
            except (AttributeError, OSError):
                freq_current = 0.0
                freq_max = 0.0

        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des données processeur: {e}")

        proc_info = ProcessorInfo(
            usage_percent=cpu_percent,
            core_count=core_count,
            logical_count=logical_count,
            frequency_current=float(freq_current) if freq_current is not None else 0.0,
            frequency_max=float(freq_max) if freq_max is not None else 0.0,
            per_core_usage=per_core_usage,
            timestamp=current_time
        )

        self._last_check = proc_info
        return proc_info

    def get_processor_info(self) -> ProcessorInfo:
        """Récupérer les informations actuelles sur le processeur.

        Méthode publique pour compatibilité avec l'ancien code.

        Returns:
            Informations détaillées sur le processeur.
        """
        return self.get_data()

    def get_usage_percentage(self) -> float:
        """Récupérer uniquement le pourcentage d'utilisation CPU.

        Returns:
            Pourcentage d'utilisation.
        """
        processor_info = self.get_data()
        return processor_info.usage_percent

    def get_core_usage(self) -> List[float]:
        """Récupérer l'utilisation par cœur.

        Returns:
            Liste des pourcentages par cœur.
        """
        processor_info = self.get_data()
        return processor_info.per_core_usage

    def get_core_count(self) -> int:
        """Récupérer le nombre de cœurs physiques.

        Returns:
            Nombre de cœurs physiques.
        """
        processor_info = self.get_data()
        return processor_info.core_count

    def get_logical_count(self) -> int:
        """Récupérer le nombre de processeurs logiques.

        Returns:
            Nombre de processeurs logiques.
        """
        processor_info = self.get_data()
        return processor_info.logical_count

    def get_frequency_info(self) -> Tuple[float, float]:
        """Récupérer les informations de fréquence.

        Returns:
            Tuple contenant (fréquence actuelle, fréquence maximale).
        """
        processor_info = self.get_data()
        return processor_info.frequency_current, processor_info.frequency_max


    def get_load_distribution(self) -> Dict[str, Any]:
        """Analyser la distribution de la charge sur les cœurs.

        Returns:
            Statistiques de distribution de charge.
        """
        core_usage = self.get_core_usage()
        
        return {
            "min_usage": min(core_usage),
            "max_usage": max(core_usage),
            "avg_usage": sum(core_usage) / len(core_usage),
            "std_deviation": self._calculate_std_dev(core_usage),
            "balanced": max(core_usage) - min(core_usage) < 20.0  # Seuil d'équilibre fixé à 20%
        }

    @staticmethod
    def _calculate_std_dev(values: List[float]) -> float:
        """Calculer l'écart-type d'une liste de valeurs.

        Args:
            values: Liste de valeurs.

        Returns:
            Écart-type.
        """
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _calculate_cpu_percent_manual(self, percpu: bool = False) -> Any:
        """Calculer manuellement le pourcentage CPU basé sur les temps CPU.

        Args:
            percpu: Si True, retourne les pourcentages par CPU.

        Returns:
            Pourcentage(s) d'utilisation CPU.
        """
        try:
            if percpu:
                current_times = psutil.cpu_times(percpu=True)
                if not self._last_per_cpu_times:
                    return [0.0] * len(current_times)
                
                percents = []
                for i, (current, last) in enumerate(zip(current_times, self._last_per_cpu_times)):
                    # Calculer le delta total en utilisant la liste pré-définie
                    total_delta = 0
                    idle_delta = 0
                    
                    for attr in self._cpu_time_attrs:
                        if hasattr(current, attr) and hasattr(last, attr):
                            try:
                                current_val = getattr(current, attr)
                                last_val = getattr(last, attr)
                                delta = current_val - last_val
                                total_delta += delta
                                if attr == 'idle':
                                    idle_delta = delta
                            except (AttributeError, TypeError):
                                continue
                    
                    if total_delta <= 0:
                        percents.append(0.0)
                    else:
                        busy_delta = total_delta - idle_delta
                        percents.append(min(100.0, max(0.0, (busy_delta / total_delta) * 100)))
                
                return percents
            else:
                current_times = psutil.cpu_times()
                if not self._last_cpu_times:
                    return 0.0
                
                # Calculer le delta total en utilisant la liste pré-définie
                total_delta = 0
                idle_delta = 0
                
                for attr in self._cpu_time_attrs:
                    if hasattr(current_times, attr) and hasattr(self._last_cpu_times, attr):
                        try:
                            current_val = getattr(current_times, attr)
                            last_val = getattr(self._last_cpu_times, attr)
                            delta = current_val - last_val
                            total_delta += delta
                            if attr == 'idle':
                                idle_delta = delta
                        except (AttributeError, TypeError):
                            continue
                
                if total_delta <= 0:
                    return 0.0
                
                busy_delta = total_delta - idle_delta
                return min(100.0, max(0.0, (busy_delta / total_delta) * 100))
                
        except (AttributeError, ZeroDivisionError, TypeError, ValueError) as e:
            # En cas d'erreur, retourner des valeurs par défaut
            self._logger.debug(f"Erreur dans le calcul CPU manuel: {e}")
            if percpu:
                return [0.0] * psutil.cpu_count()
            else:
                return 0.0


# =============================================================================
# FONCTIONS DE DÉTECTION DE FRÉQUENCE CPU
# =============================================================================

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


def _get_current_freq_from_psutil() -> Optional[float]:
    """Récupère la fréquence actuelle via psutil si disponible."""
    try:
        import psutil
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.current > 0:
            return cpu_freq.current
    except (ImportError, AttributeError):
        pass
    return None


def _get_current_freq_windows() -> Optional[float]:
    """Récupère la fréquence actuelle sur Windows."""
    # Méthode 1: PowerShell avec performance counters (plus précis)
    try:
        ps_command = r"""
        # Essayer les compteurs de performance
        try {
            $perfCounter = Get-Counter '\Processor Information(_Total)\% Processor Performance' -ErrorAction Stop
            $perfValue = $perfCounter.CounterSamples[0].CookedValue
            
            # Obtenir la fréquence max de base
            $cpu = Get-CimInstance Win32_Processor
            $maxSpeed = $cpu.MaxClockSpeed
            
            # Si on n'a pas la fréquence max, l'extraire du nom
            if (-not $maxSpeed -or $maxSpeed -eq 0 -or $maxSpeed -eq 2500) {
                $name = $cpu.Name
                if ($name -match '(\d+\.?\d*)\s*GHz') {
                    $maxSpeed = [int]([double]$matches[1] * 1000)
                }
            }
            
            # Calculer la fréquence actuelle
            if ($maxSpeed -gt 0) {
                $currentSpeed = [int](($perfValue / 100) * $maxSpeed)
                Write-Output $currentSpeed
            }
        } catch {
            # Fallback sur CurrentClockSpeed
            $cpu = Get-CimInstance Win32_Processor
            Write-Output $cpu.CurrentClockSpeed
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
            if mhz > 0:
                # Pour AMD, même 2500 peut être valide car c'est proche de 2495
                # Si on a 2500 et que la vraie max est 2495, ajuster proportionnellement
                if mhz == 2500:
                    max_freq = _get_freq_windows()
                    if max_freq and max_freq == 2495:
                        mhz = 2495  # Ajuster à la vraie valeur
                return mhz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 2: CurrentClockSpeed simple via PowerShell (plus direct)
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
                # Même logique d'ajustement AMD
                if freq == 2500:
                    max_freq = _get_freq_windows()
                    if max_freq and max_freq == 2495:
                        freq = 2495
                return freq
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 3: wmic standard (fallback)
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "CurrentClockSpeed", "/value"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.startswith('CurrentClockSpeed='):
                    mhz = int(line.split('=')[1])
                    if mhz > 0:
                        return float(mhz)
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 4: Utiliser les compteurs de performance directement
    # Essayer différents formats de performance counter (incluant versions françaises)
    counter_paths = [
        "\\Processor Information(_Total)\\% Processor Performance",
        "\\Processor(_Total)\\% Processor Time",
        "\\Informations du processeur(_Total)\\% de performance du processeur",  # Version française
        "\\Processeur(_Total)\\% temps processeur"  # Version française alternative
    ]
    
    for counter_path in counter_paths:
        try:
            result = subprocess.run(
                ["typeperf", "-sc", "1", counter_path],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ',' in line and not line.startswith('"'):
                        parts = line.split(',')
                        if len(parts) >= 2:
                            try:
                                value = float(parts[1].strip('"'))
                                
                                # Si c'est % Processor Time, c'est l'utilisation CPU, pas la performance
                                if "Processor Time" in counter_path or "temps processeur" in counter_path:
                                    # Approximation : utilisation élevée = fréquence élevée
                                    max_freq = _get_freq_windows() or 2500.0
                                    if value > 50:  # CPU utilisé à plus de 50%
                                        return max_freq
                                    else:
                                        # Estimation basée sur l'utilisation
                                        return max_freq * (0.5 + value / 200.0)  # Entre 50% et 100% de la fréquence max
                                else:
                                    # C'est un vrai counter de performance
                                    max_freq = _get_freq_windows()
                                    if max_freq:
                                        return (value / 100.0) * max_freq
                            except ValueError:
                                pass
        except (subprocess.SubprocessError, OSError, ValueError):
            pass
    
    return None


def _get_current_freq_linux() -> Optional[float]:
    """Récupère la fréquence actuelle sur Linux."""
    # Méthode 1: /sys/devices/system/cpu/
    try:
        # Essayer scaling_cur_freq (fréquence actuelle)
        cpu_cur_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
        if os.path.exists(cpu_cur_freq_path):
            with open(cpu_cur_freq_path, 'r') as f:
                khz = int(f.read().strip())
                return khz / 1000.0  # Convertir KHz en MHz
    except (OSError, IOError):
        pass
    
    # Méthode 2: /proc/cpuinfo (moyenne de tous les cœurs)
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
                # Retourner la moyenne
                return sum(cpu_mhz_values) / len(cpu_mhz_values)
    except (OSError, IOError):
        pass
    
    # Méthode 3: cpupower
    try:
        result = subprocess.run(
            ['cpupower', 'frequency-info', '-f'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Extraire la fréquence de la sortie
            for line in result.stdout.split('\n'):
                if 'current CPU frequency' in line:
                    # Format: "current CPU frequency is 2.40 GHz."
                    match = re.search(r'(\d+\.?\d*)\s*(MHz|GHz)', line)
                    if match:
                        value = float(match.group(1))
                        unit = match.group(2)
                        if unit == 'GHz':
                            return value * 1000.0
                        else:
                            return value
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_current_freq_macos() -> Optional[float]:
    """Récupère la fréquence actuelle sur macOS."""
    try:
        # sysctl pour obtenir la fréquence actuelle
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
    
    # macOS moderne peut ne pas exposer la fréquence actuelle facilement
    # Utiliser powermetrics (nécessite sudo)
    try:
        result = subprocess.run(
            ['powermetrics', '-n', '1', '-i', '1', '--samplers', 'cpu_power'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Parser la sortie pour trouver la fréquence
            for line in result.stdout.split('\n'):
                if 'CPU Average frequency' in line:
                    match = re.search(r'(\d+)\s*MHz', line)
                    if match:
                        return float(match.group(1))
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


def _get_freq_from_psutil() -> Optional[float]:
    """Récupère la fréquence via psutil si disponible."""
    try:
        import psutil
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.max > 0:
            return cpu_freq.max
    except (ImportError, AttributeError):
        pass
    return None


def _get_freq_windows() -> Optional[float]:
    """Récupère la fréquence maximale sur Windows via WMI."""
    # Méthode 1: PowerShell avec CIM (plus moderne et fiable)
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
    
    # Méthode 2: wmic avec extraction du nom si nécessaire
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "Name,MaxClockSpeed", "/value"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            max_speed = None
            cpu_name = None
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('MaxClockSpeed='):
                    try:
                        max_speed = int(line.split('=')[1])
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('Name='):
                    cpu_name = line.split('=', 1)[1]
            
            # Si on a une fréquence valide et différente de 2500
            if max_speed and max_speed > 0 and max_speed != 2500:
                return float(max_speed)
            
            # Sinon, extraire du nom
            if cpu_name:
                match = re.search(r'(\d+\.?\d*)\s*GHz', cpu_name, re.IGNORECASE)
                if match:
                    return float(match.group(1)) * 1000
                match = re.search(r'(\d+)\s*MHz', cpu_name, re.IGNORECASE)
                if match:
                    return float(match.group(1))
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 3: ProcessorNameString depuis le registre
    try:
        ps_cmd = "(Get-ItemProperty -Path 'HKLM:\\HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0' -Name 'ProcessorNameString').ProcessorNameString"
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            proc_name = result.stdout.strip()
            
            # Chercher la fréquence dans ce nom
            match = re.search(r'(\d+\.?\d*)\s*GHz', proc_name, re.IGNORECASE)
            if match:
                ghz = float(match.group(1))
                freq = ghz * 1000
                return freq
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 4: Registre Windows via PowerShell (MHz direct)
    try:
        ps_cmd = "try { $mhz = (Get-ItemProperty -Path 'HKLM:\\HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0' -Name '~MHz').'~MHz'; Write-Output $mhz } catch { Write-Output '0' }"
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            freq = float(result.stdout.strip())
            if freq > 0 and freq != 2500:
                return freq
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    # Méthode 5: Registre Windows direct (si winreg disponible)
    if platform.system() == "Windows":
        try:
            import winreg
            key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                mhz, _ = winreg.QueryValueEx(key, "~MHz")
                if mhz > 0:
                    return float(mhz)
        except (ImportError, OSError, WindowsError):
            pass
    
    return None


def _get_freq_linux() -> Optional[float]:
    """Récupère la fréquence maximale sur Linux."""
    # Méthode 1: /sys/devices/system/cpu/
    try:
        # Essayer cpuinfo_max_freq d'abord (plus précis)
        cpu_max_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
        if os.path.exists(cpu_max_freq_path):
            with open(cpu_max_freq_path, 'r') as f:
                khz = int(f.read().strip())
                return khz / 1000.0  # Convertir KHz en MHz
    except (OSError, IOError):
        pass
    
    # Méthode 2: /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            
            # Chercher "cpu MHz" max
            cpu_mhz_values = []
            for line in content.split('\n'):
                if line.startswith('cpu MHz'):
                    try:
                        mhz = float(line.split(':')[1].strip())
                        cpu_mhz_values.append(mhz)
                    except (IndexError, ValueError):
                        pass
            
            if cpu_mhz_values:
                return max(cpu_mhz_values)
    except (OSError, IOError):
        pass
    
    # Méthode 3: lscpu
    try:
        result = subprocess.run(['lscpu'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'CPU max MHz:' in line:
                    mhz = float(line.split(':')[1].strip())
                    return mhz
                elif 'CPU MHz:' in line and 'max' not in line:
                    # Fallback si pas de max MHz
                    mhz = float(line.split(':')[1].strip())
                    if mhz > 0:
                        return mhz
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    
    return None


def _get_freq_macos() -> Optional[float]:
    """Récupère la fréquence maximale sur macOS."""
    try:
        # sysctl pour obtenir la fréquence
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
        # Alternative: sysctl hw.cpufrequency
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


def _get_freq_from_processor_name() -> Optional[float]:
    """Extrait la fréquence du nom du processeur."""
    try:
        processor_name = platform.processor()
        if not processor_name:
            return None
        
        # Patterns pour extraire la fréquence
        # Ex: "Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz"
        #     "AMD Ryzen 9 5900X 12-Core Processor @ 3.7GHz"
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
