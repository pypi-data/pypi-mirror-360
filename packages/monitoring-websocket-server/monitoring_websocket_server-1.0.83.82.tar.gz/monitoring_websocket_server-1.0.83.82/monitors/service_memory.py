"""
Moniteur de mémoire interne pour surveiller l'utilisation mémoire du service lui-même.
Permet de détecter les fuites mémoire et d'analyser la croissance de la mémoire.
"""

import os
import gc
import psutil
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from collections import deque


class ServiceMemoryMonitor:
    """Surveille l'utilisation mémoire du service de monitoring."""
    
    def __init__(self, history_size: int = 1000):
        """Initialise le moniteur de mémoire.
        
        Args:
            history_size: Nombre de mesures à conserver dans l'historique
        """
        self._process = psutil.Process(os.getpid())
        self._history: deque = deque(maxlen=history_size)
        self._start_memory: Optional[float] = None
        self._peak_memory: float = 0
        self._lock = threading.Lock()
        
    def get_current_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques mémoire actuelles du processus.
        
        Returns:
            Dict contenant les statistiques mémoire détaillées
        """
        memory_info = self._process.memory_info()
        memory_percent = self._process.memory_percent()
        
        # Obtenir plus d'infos si disponibles
        try:
            memory_full = self._process.memory_full_info()
            uss = memory_full.uss  # Unique Set Size
            pss = memory_full.pss  # Proportional Set Size
        except AttributeError:
            uss = None
            pss = None
        
        # Statistiques des objets Python
        gc_stats = gc.get_stats()
        gc_counts = gc.get_count()
        
        current_memory = memory_info.rss
        
        # Mise à jour du pic mémoire
        with self._lock:
            if current_memory > self._peak_memory:
                self._peak_memory = current_memory
                
            if self._start_memory is None:
                self._start_memory = current_memory
        
        stats = {
            "timestamp": datetime.now(),
            "rss": memory_info.rss,  # Resident Set Size
            "vms": memory_info.vms,  # Virtual Memory Size
            "percent": memory_percent,
            "uss": uss,  # Unique memory
            "pss": pss,  # Proportional memory
            "peak_memory": self._peak_memory,
            "memory_growth": current_memory - (self._start_memory or current_memory),
            "gc_collections": gc_counts,  # (gen0, gen1, gen2)
            "gc_stats": gc_stats,
            "thread_count": threading.active_count(),
            "open_files": len(self._process.open_files()),
            "connections": len(self._process.net_connections()),
        }
        
        # Ajouter à l'historique
        with self._lock:
            self._history.append(stats)
        
        return stats
    
    def get_memory_trend(self, minutes: int = 60) -> Dict[str, Any]:
        """Analyse la tendance de la mémoire sur une période donnée.
        
        Args:
            minutes: Nombre de minutes à analyser
            
        Returns:
            Dict contenant l'analyse de tendance
        """
        with self._lock:
            history_copy = list(self._history)
        
        if len(history_copy) < 2:
            return {"status": "insufficient_data"}
        
        # Filtrer par temps
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        recent_data = [h for h in history_copy 
                      if h["timestamp"].timestamp() > cutoff_time]
        
        if len(recent_data) < 2:
            return {"status": "insufficient_recent_data"}
        
        # Calculer la tendance
        first_memory = recent_data[0]["rss"]
        last_memory = recent_data[-1]["rss"]
        memory_change = last_memory - first_memory
        
        # Calculer le taux de croissance
        time_diff = (recent_data[-1]["timestamp"] - recent_data[0]["timestamp"]).total_seconds()
        if time_diff > 0:
            growth_rate_per_hour = (memory_change / time_diff) * 3600
        else:
            growth_rate_per_hour = 0
        
        # Détecter les anomalies
        memory_values = [d["rss"] for d in recent_data]
        avg_memory = sum(memory_values) / len(memory_values)
        
        return {
            "status": "ok",
            "period_minutes": minutes,
            "samples": len(recent_data),
            "start_memory": first_memory,
            "current_memory": last_memory,
            "memory_change": memory_change,
            "memory_change_percent": (memory_change / first_memory * 100) if first_memory > 0 else 0,
            "growth_rate_per_hour": growth_rate_per_hour,
            "average_memory": avg_memory,
            "peak_memory": max(memory_values),
            "min_memory": min(memory_values),
            "is_growing": memory_change > 0 and abs(growth_rate_per_hour) > 1024 * 1024,  # 1MB/hour
        }
    
    def check_memory_health(self) -> Tuple[bool, List[str]]:
        """Vérifie la santé mémoire du service.
        
        Returns:
            Tuple (is_healthy, warnings)
        """
        warnings = []
        is_healthy = True
        
        stats = self.get_current_stats()
        trend = self.get_memory_trend(60)  # Dernière heure
        
        # Vérifier l'utilisation mémoire absolue
        if stats["percent"] > 80:
            warnings.append(f"Utilisation mémoire élevée: {stats['percent']:.1f}%")
            is_healthy = False
        
        # Vérifier la croissance
        if trend.get("status") == "ok" and trend.get("is_growing"):
            growth_mb_per_hour = trend["growth_rate_per_hour"] / (1024 * 1024)
            if growth_mb_per_hour > 10:  # Plus de 10MB/heure
                warnings.append(f"Croissance mémoire rapide: {growth_mb_per_hour:.1f} MB/heure")
                is_healthy = False
        
        # Vérifier les ressources
        if stats["thread_count"] > 100:
            warnings.append(f"Nombre de threads élevé: {stats['thread_count']}")
        
        if stats["open_files"] > 100:
            warnings.append(f"Nombre de fichiers ouverts élevé: {stats['open_files']}")
        
        if stats["connections"] > 1000:
            warnings.append(f"Nombre de connexions élevé: {stats['connections']}")
        
        return is_healthy, warnings
    
    def force_garbage_collection(self) -> Dict[str, Any]:
        """Force une collection complète du garbage collector.
        
        Returns:
            Statistiques avant/après la collection
        """
        before = self.get_current_stats()
        
        # Force GC sur toutes les générations
        gc.collect(2)
        
        after = self.get_current_stats()
        
        return {
            "memory_freed": before["rss"] - after["rss"],
            "memory_freed_mb": (before["rss"] - after["rss"]) / (1024 * 1024),
            "before": before,
            "after": after
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtient un résumé de l'état mémoire.
        
        Returns:
            Résumé complet de l'état mémoire
        """
        stats = self.get_current_stats()
        trend_1h = self.get_memory_trend(60)
        trend_24h = self.get_memory_trend(24 * 60)
        is_healthy, warnings = self.check_memory_health()
        
        return {
            "current": {
                "rss_mb": stats["rss"] / (1024 * 1024),
                "percent": stats["percent"],
                "peak_mb": stats["peak_memory"] / (1024 * 1024),
                "growth_mb": stats["memory_growth"] / (1024 * 1024),
            },
            "trend_1h": trend_1h,
            "trend_24h": trend_24h,
            "health": {
                "is_healthy": is_healthy,
                "warnings": warnings
            },
            "resources": {
                "threads": stats["thread_count"],
                "open_files": stats["open_files"],
                "connections": stats["connections"],
            }
        }