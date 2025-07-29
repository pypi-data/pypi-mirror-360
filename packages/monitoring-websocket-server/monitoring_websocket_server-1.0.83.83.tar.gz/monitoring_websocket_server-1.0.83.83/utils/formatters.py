"""
Formatters et utilitaires de formatage pour le système de monitoring.
Fonctions spécialisées pour formater les données système et les affichages.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from functools import lru_cache

from ..core.models import MemoryInfo, ProcessorInfo, DiskInfo, Alert, MonitoringSnapshot
from ..core.enums import AlertLevel


class DataFormatter:
    """Formatters pour les données système.
    
    Centralise toutes les fonctions de formatage pour une présentation
    cohérente des données de monitoring.
    """

    @staticmethod
    @lru_cache(maxsize=256)
    def format_bytes(bytes_value: int, precision: int = 2, 
                    binary: bool = True, unit_separator: str = " ") -> str:
        """Formate une valeur en bytes vers une unité lisible.

        Args:
            bytes_value (int): Valeur en bytes
            precision (int): Nombre de décimales
            binary (bool): Utiliser les unités binaires (1024) ou décimales (1000)
            unit_separator (str): Séparateur entre la valeur et l'unité

        Returns:
            str: Valeur formatée avec unité

        Example:
            >>> DataFormatter.format_bytes(1536, 1)
            '1.5 KB'
            >>> DataFormatter.format_bytes(1536, 1, binary=False)
            '1.5 kB'
        """
        if bytes_value == 0:
            return f"0{unit_separator}B"

        if binary:
            units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
            base = 1024
        else:
            units = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']
            base = 1000

        size = float(bytes_value)
        unit_index = 0

        while size >= base and unit_index < len(units) - 1:
            size /= base
            unit_index += 1

        return f"{size:.{precision}f}{unit_separator}{units[unit_index]}"

    @staticmethod
    def format_percentage(value: float, precision: int = 1, 
                         with_symbol: bool = True) -> str:
        """Formate un pourcentage.

        Args:
            value (float): Valeur à formater
            precision (int): Nombre de décimales
            with_symbol (bool): Inclure le symbole %

        Returns:
            str: Pourcentage formaté
        """
        symbol = "%" if with_symbol else ""
        return f"{value:.{precision}f}{symbol}"

    @staticmethod
    def format_frequency(frequency_mhz: float, precision: int = 1) -> str:
        """Formate une fréquence en MHz vers l'unité appropriée.

        Args:
            frequency_mhz (float): Fréquence en MHz
            precision (int): Nombre de décimales

        Returns:
            str: Fréquence formatée
        """
        if frequency_mhz == 0:
            return "N/A"
        
        if frequency_mhz < 1000:
            return f"{frequency_mhz:.{precision}f} MHz"
        else:
            ghz = frequency_mhz / 1000
            return f"{ghz:.{precision}f} GHz"

    @staticmethod
    def format_duration(seconds: float, compact: bool = False) -> str:
        """Formate une durée en secondes vers un format lisible.

        Args:
            seconds (float): Durée en secondes
            compact (bool): Format compact (1h2m3s) ou étendu (1 hour, 2 minutes, 3 seconds)

        Returns:
            str: Durée formatée
        """
        if seconds < 0:
            return "N/A"

        if seconds < 60:
            if compact:
                return f"{seconds:.1f}s"
            else:
                return f"{seconds:.1f} seconds"

        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60

        if minutes < 60:
            if compact:
                return f"{minutes}m{remaining_seconds:.0f}s"
            else:
                return f"{minutes} minutes, {remaining_seconds:.0f} seconds"

        hours = minutes // 60
        remaining_minutes = minutes % 60

        if hours < 24:
            if compact:
                return f"{hours}h{remaining_minutes}m"
            else:
                return f"{hours} hours, {remaining_minutes} minutes"

        days = hours // 24
        remaining_hours = hours % 24

        if compact:
            return f"{days}d{remaining_hours}h"
        else:
            return f"{days} days, {remaining_hours} hours"

    @staticmethod
    def format_timestamp(timestamp: Union[datetime, float], 
                        format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Formate un timestamp.

        Args:
            timestamp (Union[datetime, float]): Timestamp à formater
            format_string (str): Format de sortie

        Returns:
            str: Timestamp formaté
        """
        if isinstance(timestamp, float):
            timestamp = datetime.fromtimestamp(timestamp)
        
        return timestamp.strftime(format_string)

    @staticmethod
    def format_relative_time(timestamp: datetime, reference: Optional[datetime] = None) -> str:
        """Formate un timestamp relatif (il y a X minutes, etc.).

        Args:
            timestamp (datetime): Timestamp à formater
            reference (Optional[datetime]): Temps de référence (maintenant par défaut)

        Returns:
            str: Temps relatif formaté
        """
        if reference is None:
            reference = datetime.now()

        delta = reference - timestamp
        
        if delta.total_seconds() < 0:
            return "dans le futur"
        
        if delta.total_seconds() < 60:
            return f"il y a {int(delta.total_seconds())} secondes"
        elif delta.total_seconds() < 3600:
            return f"il y a {int(delta.total_seconds() // 60)} minutes"
        elif delta.total_seconds() < 86400:
            return f"il y a {int(delta.total_seconds() // 3600)} heures"
        else:
            return f"il y a {delta.days} jours"

    @staticmethod
    def format_number(number: Union[int, float], precision: int = 0, 
                     thousands_separator: str = ",") -> str:
        """Formate un nombre avec séparateurs de milliers.

        Args:
            number (Union[int, float]): Nombre à formater
            precision (int): Nombre de décimales
            thousands_separator (str): Séparateur de milliers

        Returns:
            str: Nombre formaté
        """
        if precision == 0:
            formatted = f"{int(number):,}"
        else:
            formatted = f"{number:,.{precision}f}"
        
        return formatted.replace(",", thousands_separator)


class MemoryFormatter:
    """Formatters spécialisés pour les données mémoire."""

    @staticmethod
    def format_memory_info(memory_info: MemoryInfo, detailed: bool = False) -> str:
        """Formate les informations mémoire.

        Args:
            memory_info (MemoryInfo): Informations mémoire
            detailed (bool): Affichage détaillé

        Returns:
            str: Informations formatées
        """
        used_gb = DataFormatter.format_bytes(memory_info.used)
        total_gb = DataFormatter.format_bytes(memory_info.total)
        available_gb = DataFormatter.format_bytes(memory_info.available)
        percentage = DataFormatter.format_percentage(memory_info.percentage)

        if detailed:
            return (f"Mémoire: {used_gb} / {total_gb} ({percentage}) - "
                   f"Disponible: {available_gb}")
        else:
            return f"Mémoire: {percentage} ({used_gb} / {total_gb})"

    @staticmethod
    def format_memory_usage_bar(memory_info: MemoryInfo, width: int = 20) -> str:
        """Crée une barre de progression pour l'utilisation mémoire.

        Args:
            memory_info (MemoryInfo): Informations mémoire
            width (int): Largeur de la barre

        Returns:
            str: Barre de progression
        """
        return ProgressBarFormatter.create_progress_bar(
            memory_info.percentage, 100, width
        )


class ProcessorFormatter:
    """Formatters spécialisés pour les données processeur."""

    @staticmethod
    def format_processor_info(processor_info: ProcessorInfo, detailed: bool = False) -> str:
        """Formate les informations processeur.

        Args:
            processor_info (ProcessorInfo): Informations processeur
            detailed (bool): Affichage détaillé

        Returns:
            str: Informations formatées
        """
        percentage = DataFormatter.format_percentage(processor_info.usage_percent)
        frequency = DataFormatter.format_frequency(processor_info.frequency_current)

        if detailed:
            cores_info = f"{processor_info.core_count} cœurs physiques, {processor_info.logical_count} logiques"
            return f"CPU: {percentage} @ {frequency} - {cores_info}"
        else:
            return f"CPU: {percentage} ({processor_info.core_count} cœurs)"

    @staticmethod
    def format_core_usage(processor_info: ProcessorInfo, cores_per_line: int = 4) -> str:
        """Formate l'utilisation par cœur.

        Args:
            processor_info (ProcessorInfo): Informations processeur
            cores_per_line (int): Nombre de cœurs par ligne

        Returns:
            str: Utilisation par cœur formatée
        """
        lines = []
        cores = processor_info.per_core_usage
        
        for i in range(0, len(cores), cores_per_line):
            line_cores = cores[i:i + cores_per_line]
            formatted_cores = [f"C{i+j}:{core:5.1f}%" for j, core in enumerate(line_cores)]
            lines.append(" | ".join(formatted_cores))
        
        return "\n".join(lines)


class DiskFormatter:
    """Formatters spécialisés pour les données disque."""

    @staticmethod
    def format_disk_info(disk_info: DiskInfo, detailed: bool = False) -> str:
        """Formate les informations disque.

        Args:
            disk_info (DiskInfo): Informations disque
            detailed (bool): Affichage détaillé

        Returns:
            str: Informations formatées
        """
        used_space = DataFormatter.format_bytes(disk_info.used)
        total_space = DataFormatter.format_bytes(disk_info.total)
        free_space = DataFormatter.format_bytes(disk_info.free)
        percentage = DataFormatter.format_percentage(disk_info.percentage)

        if detailed:
            return (f"Disque ({disk_info.path}): {used_space} / {total_space} ({percentage}) - "
                   f"Libre: {free_space}")
        else:
            return f"Disque: {percentage} ({free_space} libres)"


class AlertFormatter:
    """Formatters pour les alertes."""

    @staticmethod
    def format_alert(alert: Alert, include_timestamp: bool = True, 
                    include_emoji: bool = True) -> str:
        """Formate une alerte.

        Args:
            alert (Alert): Alerte à formater
            include_timestamp (bool): Inclure le timestamp
            include_emoji (bool): Inclure l'emoji

        Returns:
            str: Alerte formatée
        """
        # Emoji selon le niveau
        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🔴"
        }

        parts = []
        
        if include_emoji:
            emoji = emoji_map.get(alert.level, "")
            if emoji:
                parts.append(emoji)

        if include_timestamp:
            timestamp = DataFormatter.format_timestamp(alert.timestamp, "%H:%M:%S")
            parts.append(f"[{timestamp}]")

        level_text = alert.level.value.upper()
        parts.append(f"{level_text}:")

        parts.append(alert.message)

        return " ".join(parts)

    @staticmethod
    def format_alert_summary(alerts: List[Alert]) -> str:
        """Formate un résumé d'alertes.

        Args:
            alerts (List[Alert]): Liste d'alertes

        Returns:
            str: Résumé formaté
        """
        if not alerts:
            return "Aucune alerte"

        counts = {level: 0 for level in AlertLevel}
        for alert in alerts:
            counts[alert.level] += 1

        parts = []
        if counts[AlertLevel.CRITICAL] > 0:
            parts.append(f"🔴 {counts[AlertLevel.CRITICAL]} critique(s)")
        if counts[AlertLevel.WARNING] > 0:
            parts.append(f"⚠️ {counts[AlertLevel.WARNING]} attention")
        if counts[AlertLevel.INFO] > 0:
            parts.append(f"ℹ️ {counts[AlertLevel.INFO]} info")

        return " | ".join(parts)


class TableFormatter:
    """Formatter pour créer des tableaux ASCII."""

    @staticmethod
    def create_table(headers: List[str], rows: List[List[str]], 
                    min_width: int = 10, padding: int = 1) -> str:
        """Crée un tableau ASCII.

        Args:
            headers (List[str]): En-têtes de colonnes
            rows (List[List[str]]): Lignes de données
            min_width (int): Largeur minimale des colonnes
            padding (int): Espacement interne

        Returns:
            str: Tableau formaté
        """
        if not headers or not rows:
            return ""

        # Calcul des largeurs de colonnes
        all_rows = [headers] + rows
        col_widths = []
        
        for col_idx in range(len(headers)):
            max_width = max(len(str(row[col_idx])) if col_idx < len(row) else 0 
                           for row in all_rows)
            col_widths.append(max(max_width + 2 * padding, min_width))

        # Ligne de séparation
        separator = "+" + "+".join("-" * width for width in col_widths) + "+"

        # Construction du tableau
        lines = [separator]
        
        # En-têtes
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {header:<{col_widths[i]-2}} |"
        lines.append(header_line)
        lines.append(separator)
        
        # Lignes de données
        for row in rows:
            row_line = "|"
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    cell_str = str(cell) if cell is not None else ""
                    row_line += f" {cell_str:<{col_widths[i]-2}} |"
            lines.append(row_line)
        
        lines.append(separator)
        return "\n".join(lines)


class ProgressBarFormatter:
    """Formatter pour créer des barres de progression."""

    @staticmethod
    def create_progress_bar(current: float, maximum: float, width: int = 20,
                           filled_char: str = "█", empty_char: str = "░",
                           show_percentage: bool = True) -> str:
        """Crée une barre de progression ASCII.

        Args:
            current (float): Valeur actuelle
            maximum (float): Valeur maximale
            width (int): Largeur de la barre
            filled_char (str): Caractère pour la partie remplie
            empty_char (str): Caractère pour la partie vide
            show_percentage (bool): Afficher le pourcentage

        Returns:
            str: Barre de progression
        """
        if maximum <= 0:
            percentage = 0
        else:
            percentage = min(100.0, max(0.0, (current / maximum) * 100))

        filled_width = int(width * percentage / 100)
        empty_width = width - filled_width

        bar = filled_char * filled_width + empty_char * empty_width
        
        if show_percentage:
            return f"[{bar}] {percentage:5.1f}%"
        else:
            return f"[{bar}]"

    @staticmethod
    def create_multi_progress_bar(values: Dict[str, float], maximum: float,
                                 width: int = 20, colors: Optional[Dict[str, str]] = None) -> str:
        """Crée une barre de progression multi-segments.

        Args:
            values (Dict[str, float]): Valeurs par segment
            maximum (float): Valeur maximale totale
            width (int): Largeur totale
            colors (Optional[Dict[str, str]]): Couleurs par segment

        Returns:
            str: Barre multi-segments
        """
        if maximum <= 0:
            return "░" * width

        total_current = sum(values.values())
        if total_current <= 0:
            return "░" * width

        # Caractères par défaut pour les segments
        default_chars = ["█", "▓", "▒", "░"]
        
        bar_chars = []
        
        for i, (name, value) in enumerate(values.items()):
            segment_width = int(width * value / maximum)
            char = colors.get(name, default_chars[i % len(default_chars)]) if colors else default_chars[i % len(default_chars)]
            bar_chars.extend([char] * segment_width)

        # Remplir le reste avec des espaces vides
        remaining = width - len(bar_chars)
        bar_chars.extend(["░"] * remaining)

        return "".join(bar_chars[:width])


class SystemSummaryFormatter:
    """Formatter pour les résumés système complets."""

    @staticmethod
    def format_system_summary(snapshot: MonitoringSnapshot, 
                            compact: bool = False, include_alerts: bool = True) -> str:
        """Formate un résumé système complet.

        Args:
            snapshot (MonitoringSnapshot): Snapshot système
            compact (bool): Format compact
            include_alerts (bool): Inclure les alertes

        Returns:
            str: Résumé formaté
        """
        if compact:
            return SystemSummaryFormatter._format_compact_summary(snapshot, include_alerts)
        else:
            return SystemSummaryFormatter._format_detailed_summary(snapshot, include_alerts)

    @staticmethod
    def _format_compact_summary(snapshot: MonitoringSnapshot, include_alerts: bool) -> str:
        """Formate un résumé compact."""
        timestamp = DataFormatter.format_timestamp(snapshot.timestamp, "%H:%M:%S")
        
        mem_pct = DataFormatter.format_percentage(snapshot.memory_info.percentage)
        cpu_pct = DataFormatter.format_percentage(snapshot.processor_info.usage_percent)
        disk_pct = DataFormatter.format_percentage(snapshot.disk_info.percentage)
        
        summary = f"[{timestamp}] MEM:{mem_pct} CPU:{cpu_pct} DISK:{disk_pct}"
        
        if include_alerts and snapshot.alerts:
            alert_summary = AlertFormatter.format_alert_summary(snapshot.alerts)
            summary += f" | {alert_summary}"
        
        return summary

    @staticmethod
    def _format_detailed_summary(snapshot: MonitoringSnapshot, include_alerts: bool) -> str:
        """Formate un résumé détaillé."""
        lines = []
        
        # En-tête avec timestamp
        timestamp = DataFormatter.format_timestamp(snapshot.timestamp)
        lines.append(f"=== Résumé Système - {timestamp} ===")
        lines.append("")
        
        # Informations mémoire
        mem_info = MemoryFormatter.format_memory_info(snapshot.memory_info, detailed=True)
        mem_bar = MemoryFormatter.format_memory_usage_bar(snapshot.memory_info)
        lines.append(f"🧠 {mem_info}")
        lines.append(f"   {mem_bar}")
        lines.append("")
        
        # Informations processeur
        cpu_info = ProcessorFormatter.format_processor_info(snapshot.processor_info, detailed=True)
        cpu_bar = ProgressBarFormatter.create_progress_bar(snapshot.processor_info.usage_percent, 100)
        lines.append(f"⚡ {cpu_info}")
        lines.append(f"   {cpu_bar}")
        lines.append("")
        
        # Informations disque
        disk_info = DiskFormatter.format_disk_info(snapshot.disk_info, detailed=True)
        disk_bar = ProgressBarFormatter.create_progress_bar(snapshot.disk_info.percentage, 100)
        lines.append(f"💾 {disk_info}")
        lines.append(f"   {disk_bar}")
        lines.append("")
        
        # Alertes
        if include_alerts:
            if snapshot.alerts:
                lines.append("🚨 Alertes actives:")
                for alert in snapshot.alerts[-5:]:  # 5 dernières alertes
                    alert_text = AlertFormatter.format_alert(alert, include_timestamp=True)
                    lines.append(f"   {alert_text}")
            else:
                lines.append("✅ Aucune alerte active")
            lines.append("")
        
        return "\n".join(lines)


class JSONFormatter:
    """Formatter pour la sortie JSON structurée."""

    @staticmethod
    def format_snapshot_for_api(snapshot: MonitoringSnapshot) -> Dict[str, Any]:
        """Formate un snapshot pour une API JSON.

        Args:
            snapshot (MonitoringSnapshot): Snapshot à formater

        Returns:
            Dict[str, Any]: Données formatées pour JSON
        """
        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "system": {
                "memory": {
                    "usage_percent": round(snapshot.memory_info.percentage, 2),
                    "used_bytes": snapshot.memory_info.used,
                    "total_bytes": snapshot.memory_info.total,
                    "available_bytes": snapshot.memory_info.available,
                    "used_human": DataFormatter.format_bytes(snapshot.memory_info.used),
                    "total_human": DataFormatter.format_bytes(snapshot.memory_info.total)
                },
                "cpu": {
                    "usage_percent": round(snapshot.processor_info.usage_percent, 2),
                    "core_count": snapshot.processor_info.core_count,
                    "logical_count": snapshot.processor_info.logical_count,
                    "frequency_mhz": round(snapshot.processor_info.frequency_current, 1),
                    "frequency_human": DataFormatter.format_frequency(snapshot.processor_info.frequency_current),
                    "per_core_usage": [round(usage, 1) for usage in snapshot.processor_info.per_core_usage]
                },
                "disk": {
                    "usage_percent": round(snapshot.disk_info.percentage, 2),
                    "used_bytes": snapshot.disk_info.used,
                    "total_bytes": snapshot.disk_info.total,
                    "free_bytes": snapshot.disk_info.free,
                    "path": snapshot.disk_info.path,
                    "used_human": DataFormatter.format_bytes(snapshot.disk_info.used),
                    "total_human": DataFormatter.format_bytes(snapshot.disk_info.total),
                    "free_human": DataFormatter.format_bytes(snapshot.disk_info.free)
                }
            },
            "alerts": [
                {
                    "level": alert.level.value,
                    "component": alert.component,
                    "message": alert.message,
                    "value": round(alert.value, 2),
                    "threshold": round(alert.threshold, 2),
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in snapshot.alerts
            ],
            "alert_count": len(snapshot.alerts)
        }


class ConfigFormatter:
    """Formatter pour les configurations et paramètres."""

    @staticmethod
    def format_config_table(config_dict: Dict[str, Any], 
                           title: str = "Configuration") -> str:
        """Formate une configuration sous forme de tableau.

        Args:
            config_dict (Dict[str, Any]): Configuration à formater
            title (str): Titre du tableau

        Returns:
            str: Configuration formatée
        """
        def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
            """Aplatit un dictionnaire imbriqué."""
            items: List[Tuple[str, Any]] = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        flat_config = flatten_dict(config_dict)
        
        # Préparation des données pour le tableau
        headers = ["Paramètre", "Valeur", "Type"]
        rows = []
        
        for key, value in sorted(flat_config.items()):
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            
            rows.append([key, value_str, type(value).__name__])
        
        table = TableFormatter.create_table(headers, rows)
        return f"{title}\n{table}"
