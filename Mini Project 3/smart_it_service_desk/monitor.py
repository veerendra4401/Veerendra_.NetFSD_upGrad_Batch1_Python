"""
monitor.py - System Monitoring Module
Automated ITIL Service Desk System

Demonstrates:
  - OOP: Monitor class with instance variables and methods
  - psutil for CPU / Memory / Disk / Network monitoring
  - Auto-ticket creation on threshold breach
  - Generator-based alert streaming
  - Scheduled periodic monitoring (threading-based)
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generator, List, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from logger import get_logger
from utils import audit_log, now_str, timer

log = get_logger("monitor")

# ─────────────────────────────────────────────
# Thresholds
# ─────────────────────────────────────────────

CPU_THRESHOLD    = 90.0   # %
RAM_THRESHOLD    = 95.0   # %
DISK_THRESHOLD   = 10.0   # % free
NET_THRESHOLD_MB = 100.0  # MB/s  (just for demonstration)


# ─────────────────────────────────────────────
# Alert dataclass
# ─────────────────────────────────────────────

@dataclass
class Alert:
    """Represents a single monitoring alert."""
    alert_type:  str
    metric:      str
    value:       float
    threshold:   float
    message:     str
    severity:    str = "P1"
    timestamp:   str = field(default_factory=now_str)
    ticket_id:   Optional[str] = None

    def __str__(self) -> str:
        return (
            f"[{self.timestamp}] {self.severity} ALERT | {self.alert_type} | "
            f"{self.metric}: {self.value:.1f}  (threshold: {self.threshold}) | {self.message}"
        )


# ─────────────────────────────────────────────
# Monitor Class
# ─────────────────────────────────────────────

class Monitor:
    """
    System resource monitor.

    Methods:
      sample()              – take one snapshot of all metrics
      check_thresholds()    – compare metrics and return Alert list
      alert_generator()     – generator that yields alerts on each check
      start_background()    – launch a daemon thread for periodic monitoring
      stop()                – stop the background thread
    """

    def __init__(
        self,
        cpu_threshold:  float = CPU_THRESHOLD,
        ram_threshold:  float = RAM_THRESHOLD,
        disk_threshold: float = DISK_THRESHOLD,
        poll_interval:  int   = 60,   # seconds between background polls
        ticket_manager = None,        # optional TicketManager for auto-tickets
    ):
        self._cpu_threshold  = cpu_threshold
        self._ram_threshold  = ram_threshold
        self._disk_threshold = disk_threshold
        self._poll_interval  = poll_interval
        self._ticket_manager = ticket_manager

        self._alerts_history: List[Alert] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ── Metric Sampling ───────────────────────────────────────

    @timer
    def sample(self) -> dict:
        """
        Collect a snapshot of current system metrics.
        Falls back to simulated values if psutil is unavailable.
        """
        if PSUTIL_AVAILABLE:
            cpu  = psutil.cpu_percent(interval=1)
            ram  = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            disk_free_pct = 100.0 - disk

            # Network bytes sent/recv since boot
            net_io = psutil.net_io_counters()
            net_mb = round((net_io.bytes_sent + net_io.bytes_recv) / (1024 ** 2), 2)
        else:
            # Simulated metrics for environments without psutil
            import random
            cpu         = random.uniform(20, 100)
            ram         = random.uniform(40, 98)
            disk_free_pct = random.uniform(5, 50)
            net_mb      = random.uniform(10, 200)
            log.debug("psutil unavailable — using simulated metrics.")

        snapshot = {
            "timestamp":     now_str(),
            "cpu_percent":   cpu,
            "ram_percent":   ram,
            "disk_free_pct": disk_free_pct,
            "network_mb":    net_mb,
        }
        log.debug(
            "Metrics — CPU: %.1f%%, RAM: %.1f%%, Disk Free: %.1f%%, Net: %.1f MB",
            cpu, ram, disk_free_pct, net_mb,
        )
        return snapshot

    # ── Threshold Checking ────────────────────────────────────

    def check_thresholds(self, snapshot: Optional[dict] = None) -> List[Alert]:
        """
        Compare a metrics snapshot against thresholds.
        Returns a list of Alert objects for any metric that has breached.
        Optionally auto-creates tickets via TicketManager.
        """
        if snapshot is None:
            snapshot = self.sample()

        alerts: List[Alert] = []

        # CPU check
        if snapshot["cpu_percent"] > self._cpu_threshold:
            alert = Alert(
                alert_type = "CPU",
                metric     = "cpu_percent",
                value      = snapshot["cpu_percent"],
                threshold  = self._cpu_threshold,
                message    = f"CPU usage critical: {snapshot['cpu_percent']:.1f}%",
                severity   = "P1",
            )
            alerts.append(alert)
            log.critical("[MONITOR] %s", alert)

        # RAM check
        if snapshot["ram_percent"] > self._ram_threshold:
            alert = Alert(
                alert_type = "RAM",
                metric     = "ram_percent",
                value      = snapshot["ram_percent"],
                threshold  = self._ram_threshold,
                message    = f"RAM usage critical: {snapshot['ram_percent']:.1f}%",
                severity   = "P1",
            )
            alerts.append(alert)
            log.critical("[MONITOR] %s", alert)

        # Disk check (free %)
        if snapshot["disk_free_pct"] < self._disk_threshold:
            alert = Alert(
                alert_type = "DISK",
                metric     = "disk_free_pct",
                value      = snapshot["disk_free_pct"],
                threshold  = self._disk_threshold,
                message    = f"Disk free critically low: {snapshot['disk_free_pct']:.1f}%",
                severity   = "P1",
            )
            alerts.append(alert)
            log.critical("[MONITOR] %s", alert)

        # Auto-create tickets for each alert
        if self._ticket_manager and alerts:
            for alert in alerts:
                self._auto_create_ticket(alert)

        self._alerts_history.extend(alerts)
        return alerts

    @audit_log("Auto Create Monitor Ticket")
    def _auto_create_ticket(self, alert: Alert) -> None:
        """Automatically raise a P1 incident ticket for a monitoring alert."""
        try:
            ticket = self._ticket_manager.create_ticket(
                employee_name     = "System Monitor",
                department        = "IT Infrastructure",
                issue_description = alert.message,
                category          = f"System Alert - {alert.alert_type}",
                ticket_type       = "IncidentTicket",
                priority          = "P1",
                impact            = "High",
                urgency           = "High",
            )
            alert.ticket_id = ticket.ticket_id
            log.info("[MONITOR] Auto-ticket created: %s", ticket.ticket_id)
        except Exception as exc:
            log.error("[MONITOR] Failed to create auto-ticket: %s", exc)

    # ── Generator ─────────────────────────────────────────────

    def alert_generator(self, max_checks: int = 10) -> Generator[List[Alert], None, None]:
        """
        Generator that yields the alert list from each periodic check.
        Demonstrates the generator pattern.
        """
        for _ in range(max_checks):
            alerts = self.check_thresholds()
            yield alerts
            time.sleep(self._poll_interval)

    # ── Background Thread ─────────────────────────────────────

    def _background_loop(self) -> None:
        """Target function for the monitoring daemon thread."""
        log.info("[MONITOR] Background monitoring started (interval: %ds).", self._poll_interval)
        while self._running:
            try:
                self.check_thresholds()
            except Exception as exc:
                log.error("[MONITOR] Error during background check: %s", exc)
            # Sleep in small chunks so stop() is responsive
            for _ in range(self._poll_interval * 10):
                if not self._running:
                    break
                time.sleep(0.1)
        log.info("[MONITOR] Background monitoring stopped.")

    def start_background(self) -> None:
        """Launch the monitoring daemon thread."""
        if self._running:
            log.warning("[MONITOR] Already running.")
            return
        self._running = True
        self._thread = threading.Thread(target=self._background_loop, daemon=True, name="MonitorThread")
        self._thread.start()
        log.info("[MONITOR] Daemon thread started: %s", self._thread.name)

    def stop(self) -> None:
        """Gracefully stop the background monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        log.info("[MONITOR] Stopped.")

    # ── History ───────────────────────────────────────────────

    @property
    def alerts_history(self) -> List[Alert]:
        """Return all alerts collected since this Monitor was created."""
        return list(self._alerts_history)

    def alerts_since(self, since_str: str) -> List[Alert]:
        """Return alerts that occurred after a given datetime string."""
        from utils import parse_datetime
        cutoff = parse_datetime(since_str)
        return [a for a in self._alerts_history if parse_datetime(a.timestamp) >= cutoff]

    # ── Display ───────────────────────────────────────────────

    def display_snapshot(self, snapshot: Optional[dict] = None) -> None:
        """Pretty-print the current system metrics snapshot."""
        if snapshot is None:
            snapshot = self.sample()
        print("=" * 60)
        print("  SYSTEM HEALTH SNAPSHOT")
        print(f"  Timestamp   : {snapshot['timestamp']}")
        print(f"  CPU Usage   : {snapshot['cpu_percent']:.1f}%  (threshold: {self._cpu_threshold}%)")
        print(f"  RAM Usage   : {snapshot['ram_percent']:.1f}%  (threshold: {self._ram_threshold}%)")
        print(f"  Disk Free   : {snapshot['disk_free_pct']:.1f}%  (threshold: {self._disk_threshold}%)")
        print(f"  Network I/O : {snapshot['network_mb']:.1f} MB")
        print("=" * 60)
