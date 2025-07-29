"""
Utilitaires d'affichage pour le système de monitoring.
Gestion de l'affichage console et formatage visuel.
"""

import os
import sys
from typing import Dict, Any, List

from ..core.models import Alert
from ..config import (
    MEMORY_WARNING_THRESHOLD, MEMORY_CRITICAL_THRESHOLD,
    DISK_WARNING_THRESHOLD, DISK_CRITICAL_THRESHOLD
)


class DisplayManager:
    """Gestionnaire des fonctionnalités d'affichage."""

    def __init__(self) -> None:
        """Initialise le gestionnaire d'affichage."""
        self._clear_supported: bool = self._test_clear_screen()

    @property
    def clear_supported(self) -> bool:
        """Indique si le clear screen est supporté.

        Returns:
            bool: True si supporté
        """
        return self._clear_supported

    @staticmethod
    def _test_clear_screen() -> bool:
        """Teste si le clear screen fonctionne dans l'environnement actuel.

        Returns:
            bool: True si le clear screen fonctionne
        """
        try:
            # Test simple : vérifier si on est dans un vrai terminal
            if not sys.stdout.isatty():
                return False

            # Test des capacités ANSI
            if os.name == 'nt':
                # Windows : vérifier si on supporte ANSI
                try:
                    import colorama
                    return True
                except ImportError:
                    return False
            else:
                # Unix/Linux : généralement supporté
                return os.environ.get('TERM') != 'dumb'
        except (AttributeError, KeyError, OSError):
            return False

    def clear_screen(self) -> None:
        """Efface l'écran seulement si c'est supporté."""
        if not self._clear_supported:
            return

        try:
            # Séquences d'échappement ANSI multiples
            print('\033[2J\033[1;1H', end='', flush=True)
            print('\033[H\033[2J', end='', flush=True)
            print('\x1b[2J\x1b[H', end='', flush=True)
        except (OSError, IOError):
            try:
                # Commandes système en fallback
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            except (OSError, IOError):
                pass  # Silencieux si ça échoue

    @staticmethod
    def print_header(title: str = "REAL-TIME SYSTEM MONITORING SERVICE") -> None:
        """Affiche l'en-tête du monitoring.

        Args:
            title (str): Titre à afficher
        """
        print("=" * 80)
        print(f"🖥️  {title}".center(80))
        print("=" * 80)

    @staticmethod
    def print_separator(char: str = "-", length: int = 80) -> None:
        """Affiche un séparateur visuel.

        Args:
            char (str): Caractère du séparateur
            length (int): Longueur du séparateur
        """
        print(char * length)

    @staticmethod
    def print_compact_header(iteration: int, timestamp: str) -> None:
        """Affiche un en-tête compact pour mode IDE.

        Args:
            iteration (int): Numéro d'itération
            timestamp (str): Timestamp formaté
        """
        print(f"🖥️ MONITORING #{iteration:,} | {timestamp} | Ctrl+C to stop")
        print("=" * 80)

    @staticmethod
    def print_compact_metrics(data: Dict[str, Any]) -> None:
        """Affiche les métriques de manière compacte sur une ligne.

        Args:
            data (Dict[str, Any]): Données système
        """
        # Extraction des métriques
        mem_percent = data['memory']['usage_percent']
        cpu_percent = data['cpu']['usage_percent']
        disk_percent = data['disk']['usage_percent']

        # Émojis de statut
        mem_emoji = "🟢" if mem_percent < MEMORY_WARNING_THRESHOLD else "🟡" if mem_percent < MEMORY_CRITICAL_THRESHOLD else "🔴"
        cpu_emoji = "🟢"  # Pas de seuils d'alerte pour le CPU
        disk_emoji = "🟢" if disk_percent < DISK_WARNING_THRESHOLD else "🟡" if disk_percent < DISK_CRITICAL_THRESHOLD else "🔴"
        alert_emoji = "✅" if data['alerts'] == 0 else f"🚨{data['alerts']}"

        # Affichage compact
        print(f"{mem_emoji} MEM: {mem_percent:5.1f}% | "
              f"{cpu_emoji} CPU: {cpu_percent:5.1f}% | "
              f"{disk_emoji} DISK: {disk_percent:5.1f}% | "
              f"{alert_emoji} Alertes")

    def print_detailed_metrics(self, data: Dict[str, Any]) -> None:
        """Affiche les métriques de manière détaillée.

        Args:
            data (Dict[str, Any]): Données système
        """
        print("📊 SYSTEM METRICS:")
        self.print_separator()

        # Mémoire
        mem_percent = data['memory']['usage_percent']
        mem_emoji = "🟢" if mem_percent < MEMORY_WARNING_THRESHOLD else "🟡" if mem_percent < MEMORY_CRITICAL_THRESHOLD else "🔴"
        print(f"{mem_emoji} Memory:     {mem_percent:6.1f}% "
              f"({data['memory']['used_gb']:6.1f} / {data['memory']['total_gb']:6.1f} GB)")

        # CPU
        cpu_percent = data['cpu']['usage_percent']
        cpu_emoji = "🟢"  # Pas de seuils d'alerte pour le CPU
        print(f"{cpu_emoji} CPU:        {cpu_percent:6.1f}% "
              f"({data['cpu']['core_count']} cores)")

        # Disque
        disk_percent = data['disk']['usage_percent']
        disk_emoji = "🟢" if disk_percent < DISK_WARNING_THRESHOLD else "🟡" if disk_percent < DISK_CRITICAL_THRESHOLD else "🔴"
        print(f"{disk_emoji} Disk:       {disk_percent:6.1f}% "
              f"({data['disk']['free_gb']:6.1f} GB free)")

    def print_alerts_section(self, alerts: List[Alert], recent_alerts: List[Alert]) -> None:
        """Affiche la section des alertes.

        Args:
            alerts (List[Alert]): Liste des alertes actuelles
            recent_alerts (List[Alert]): Alertes récentes
        """
        alert_count = len(alerts)
        if alert_count > 0:
            print("🚨 ACTIVE ALERTS:")
            self.print_separator()
            for alert in recent_alerts[-5:]:
                level_emoji = "⚠️" if alert.level.value == "warning" else "🔴"
                print(f"{level_emoji} {alert.timestamp.strftime('%H:%M:%S')} | {alert.message}")
            print()
        else:
            print("✅ No active alerts")
            print()

    def print_statistics_section(self, stats: Dict[str, Any]) -> None:
        """Affiche la section des statistiques.

        Args:
            stats (Dict[str, Any]): Statistiques du service
        """
        print("📈 STATISTICS:")
        self.print_separator()
        print(f"🚨 Alerts generated:       {stats.get('alerts_count', 0):,}")
        
        start_time = stats.get('start_time')
        if start_time:
            from datetime import datetime
            uptime = datetime.now() - start_time
            uptime_str = str(uptime).split('.')[0]
            print(f"⏱️  Uptime:                 {uptime_str}")
