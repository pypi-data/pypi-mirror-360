"""
Moniteur de carte graphique (GPU).
Surveillance de l'utilisation du GPU et de ses caractéristiques.
"""

import logging
import subprocess
from typing import Optional, List, Any
from dataclasses import dataclass

from .base import BaseMonitor


@dataclass
class GPUInfo:
    """Informations sur la carte graphique."""
    name: str
    driver_version: str
    memory_total: int  # En octets
    memory_used: int   # En octets
    memory_free: int   # En octets
    memory_percentage: float
    gpu_usage_percent: float
    temperature: Optional[float]  # En Celsius
    power_draw: Optional[float]   # En Watts
    power_limit: Optional[float]  # En Watts


class GPUMonitor(BaseMonitor):
    """Moniteur pour surveiller l'utilisation de la carte graphique."""

    def __init__(self) -> None:
        """Initialise le moniteur GPU."""
        super().__init__("GPU")
        self._gpu_available: bool = False
        self._nvidia_smi_available: bool = False
        self._pynvml_available: bool = False
        self._logger: logging.Logger = logging.getLogger(__name__)
        
        # Tentative d'import des bibliothèques GPU
        self._try_import_gpu_libs()
        
    def _try_import_gpu_libs(self) -> None:
        """Tente d'importer les bibliothèques GPU disponibles."""
        # Essayer GPUtil (plus simple)
        try:
            import GPUtil
            self._gputil: Any = GPUtil
            self._gpu_available = True
            self._logger.info("GPUtil disponible pour le monitoring GPU")
        except ImportError:
            import GPUtil
            self._gputil: Any = None
            
        # Essayer pynvml (NVIDIA Management Library)
        try:
            import pynvml
            self._pynvml: Any = pynvml
            self._pynvml_available = True
            self._logger.info("pynvml disponible pour le monitoring GPU NVIDIA")
        except ImportError:
            import pynvml
            self._pynvml: Any = None
            
        # Vérifier nvidia-smi (ligne de commande)
        try:
            result = subprocess.run(['nvidia-smi', '--help'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=2)
            if result.returncode == 0:
                self._nvidia_smi_available = True
                self._logger.info("nvidia-smi disponible pour le monitoring GPU")
        except (ImportError, FileNotFoundError):
            pass
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
            # Pour les autres exceptions liées à subprocess
            pass
    
    def _do_initialize(self) -> None:
        """Initialise le moniteur GPU."""
        # Si GPUtil est disponible, c'est suffisant
        if self._gputil:
            try:
                # Tester si des GPUs sont détectés
                gpus = self._gputil.getGPUs()
                if gpus:
                    self._gpu_available = True
                    self._logger.info(f"GPU détecté via GPUtil: {gpus[0].name}")
                else:
                    self._logger.info("GPUtil installé mais aucun GPU détecté")
            except Exception as e:
                self._logger.debug(f"Erreur GPUtil lors de l'initialisation: {e}")
        
        # Essayer pynvml si GPUtil n'a pas fonctionné
        if not self._gpu_available and self._pynvml_available and self._pynvml:
            try:
                self._pynvml.nvmlInit()
                device_count = self._pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    self._gpu_available = True
                    self._logger.info(f"GPU détecté via pynvml: {device_count} GPU(s)")
            except Exception as e:
                self._logger.debug(f"Impossible d'initialiser pynvml: {e}")
                
        if not self._gpu_available and not self._gputil and not self._pynvml_available:
            self._logger.warning("Aucune bibliothèque GPU disponible. Installez GPUtil ou pynvml.")
    
    def _collect_data(self) -> Optional[GPUInfo]:
        """Collecte les informations sur le GPU.

        Returns:
            Optional[GPUInfo]: Informations GPU ou None si pas de GPU
        """
        # Essayer GPUtil d'abord (plus simple)
        if self._gputil and self._gpu_available:
            try:
                gpus = self._gputil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Prendre le premier GPU
                    return GPUInfo(
                        name=gpu.name,
                        driver_version=gpu.driver,
                        memory_total=int(gpu.memoryTotal * 1024 * 1024),  # MB to bytes
                        memory_used=int(gpu.memoryUsed * 1024 * 1024),
                        memory_free=int(gpu.memoryFree * 1024 * 1024),
                        memory_percentage=gpu.memoryUtil * 100,
                        gpu_usage_percent=gpu.load * 100,
                        temperature=gpu.temperature,
                        power_draw=None,  # GPUtil ne fournit pas cette info
                        power_limit=None
                    )
            except Exception as e:
                self._logger.debug(f"Erreur GPUtil: {e}")
        
        # Essayer pynvml ensuite (plus détaillé)
        if self._pynvml_available and self._pynvml:
            try:
                device_count = self._pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = self._pynvml.nvmlDeviceGetHandleByIndex(0)
                    
                    # Informations de base
                    name = self._pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                    
                    # Driver
                    driver = self._pynvml.nvmlSystemGetDriverVersion().decode('utf-8')
                    
                    # Mémoire
                    mem_info = self._pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    # Utilisation
                    utilization = self._pynvml.nvmlDeviceGetUtilizationRates(handle)
                    
                    # Température
                    try:
                        temp: Optional[float] = float(self._pynvml.nvmlDeviceGetTemperature(handle, 
                                                                    self._pynvml.NVML_TEMPERATURE_GPU))
                    except (AttributeError, RuntimeError, ValueError):
                        temp = None
                    
                    # Consommation
                    try:
                        power = self._pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # mW to W
                        power_limit = self._pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0
                    except (AttributeError, RuntimeError, ValueError):
                        power = None
                        power_limit = None
                    
                    return GPUInfo(
                        name=name,
                        driver_version=driver,
                        memory_total=mem_info.total,
                        memory_used=mem_info.used,
                        memory_free=mem_info.free,
                        memory_percentage=(mem_info.used / mem_info.total) * 100,
                        gpu_usage_percent=float(utilization.gpu),
                        temperature=temp,
                        power_draw=power,
                        power_limit=power_limit
                    )
            except Exception as e:
                self._logger.debug(f"Erreur pynvml: {e}")
        
        # Essayer nvidia-smi en dernier recours
        if self._nvidia_smi_available:
            try:
                import xml.etree.ElementTree as Et
                
                result = subprocess.run(
                    ['nvidia-smi', '-q', '-x'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    root = Et.fromstring(result.stdout)
                    gpu = root.find('gpu')
                    
                    if gpu is not None:
                        # Parser les informations XML
                        name_elem = gpu.find('product_name')
                        name: str = name_elem.text if name_elem is not None else "Unknown"
                        driver_elem = root.find('driver_version')
                        driver: str = driver_elem.text if driver_elem is not None else "N/A"
                        
                        # Mémoire
                        fb_memory = gpu.find('fb_memory_usage')
                        if fb_memory is not None:
                            total_elem = fb_memory.find('total')
                            used_elem = fb_memory.find('used')
                            free_elem = fb_memory.find('free')
                            total: int = int(total_elem.text.split()[0]) * 1024 * 1024 if total_elem is not None else 0
                            used: int = int(used_elem.text.split()[0]) * 1024 * 1024 if used_elem is not None else 0
                            free: int = int(free_elem.text.split()[0]) * 1024 * 1024 if free_elem is not None else 0
                        else:
                            total = used = free = 0
                        
                        # Utilisation
                        utilization = gpu.find('utilization')
                        if utilization is not None:
                            gpu_util_elem = utilization.find('gpu_util')
                            gpu_util: float = float(gpu_util_elem.text.split()[0]) if gpu_util_elem is not None else 0.0
                        else:
                            gpu_util = 0.0
                        
                        # Température
                        temp_value: Optional[float] = None
                        temp_section = gpu.find('temperature')
                        if temp_section is not None:
                            gpu_temp_elem = temp_section.find('gpu_temp')
                            if gpu_temp_elem is not None:
                                try:
                                    temp_value = float(gpu_temp_elem.text.split()[0])
                                except (ValueError, IndexError):
                                    temp_value = None
                        
                        return GPUInfo(
                            name=name,
                            driver_version=driver,
                            memory_total=total,
                            memory_used=used,
                            memory_free=free,
                            memory_percentage=(used / total) * 100,
                            gpu_usage_percent=gpu_util,
                            temperature=temp_value,
                            power_draw=None,
                            power_limit=None
                        )
            except Exception as e:
                self._logger.debug(f"Erreur nvidia-smi: {e}")
        
        # Aucune méthode n'a fonctionné, retourner des données factices
        return GPUInfo(
            name="Aucun GPU détecté",
            driver_version="N/A",
            memory_total=0,
            memory_used=0,
            memory_free=0,
            memory_percentage=0.0,
            gpu_usage_percent=0.0,
            temperature=None,
            power_draw=None,
            power_limit=None
        )
    
    def get_gpu_info(self) -> Optional[GPUInfo]:
        """Récupère les informations actuelles sur le GPU.

        Returns:
            Optional[GPUInfo]: Informations GPU ou None
        """
        return self.get_data()
    
    def is_gpu_available(self) -> bool:
        """Vérifie si un GPU est disponible.

        Returns:
            bool: True si un GPU est détecté
        """
        return self._gpu_available
    
    def get_gpu_count(self) -> int:
        """Retourne le nombre de GPUs détectés.

        Returns:
            int: Nombre de GPUs
        """
        if self._gputil and self._gpu_available:
            try:
                return len(self._gputil.getGPUs())
            except (AttributeError, RuntimeError, ValueError):
                pass
                
        if self._pynvml_available and self._pynvml:
            try:
                return self._pynvml.nvmlDeviceGetCount()
            except (AttributeError, RuntimeError, ValueError):
                pass
                
        return 0
    
    def get_all_gpus_info(self) -> List[GPUInfo]:
        """Récupère les informations sur tous les GPUs.

        Returns:
            List[GPUInfo]: Liste des informations pour chaque GPU
        """
        gpus_info = []
        
        if self._gputil and self._gpu_available:
            try:
                gpus = self._gputil.getGPUs()
                for gpu in gpus:
                    info = GPUInfo(
                        name=gpu.name,
                        driver_version=gpu.driver,
                        memory_total=int(gpu.memoryTotal * 1024 * 1024),
                        memory_used=int(gpu.memoryUsed * 1024 * 1024),
                        memory_free=int(gpu.memoryFree * 1024 * 1024),
                        memory_percentage=gpu.memoryUtil * 100,
                        gpu_usage_percent=gpu.load * 100,
                        temperature=gpu.temperature,
                        power_draw=None,
                        power_limit=None
                    )
                    gpus_info.append(info)
            except Exception as e:
                self._logger.debug(f"Erreur lors de la récupération de tous les GPUs: {e}")
        
        return gpus_info if gpus_info else [self._collect_data()]