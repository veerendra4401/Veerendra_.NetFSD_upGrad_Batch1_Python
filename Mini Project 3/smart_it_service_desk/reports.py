"""
reports.py - Reports Module
Automated ITIL Service Desk System

Implements:
  ReportGenerator class (OOP)
  Daily Report  — totals, open/closed, high-priority, SLA breaches
  Monthly Report — most common issue, avg resolution time, dept breakdown
  Export to console and optionally to JSON/CSV
"""

import csv
import json
import os
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from logger import get_logger
from tickets import Ticket, TicketManager
from utils import (
    audit_log,
    average_resolution_hours,
    count_by_priority,
    now_str,
    parse_datetime,
    timer,
    center_banner,
)

log = get_logger("reports")

DATA_DIR     = os.path.join(os.path.dirname(__file__), "data")
REPORTS_DIR  = os.path.join(DATA_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# ReportGenerator Class
# ═══════════════════════════════════════════════════════════════

class ReportGenerator:
    """
    Generates Daily and Monthly service-desk reports.

    Demonstrates:
      - OOP (class, instance variables, methods)
      - map / filter / Counter (functional style)
      - File handling (write JSON and CSV reports)
      - Special method __str__
    """

    def __init__(self, ticket_manager: TicketManager):
        self._tm = ticket_manager

    def __str__(self) -> str:
        stats = self._tm.summary_stats()
        return f"ReportGenerator | Total Tickets: {stats['total']} | Open: {stats['open']}"

    # ── Helper: filter by date range ─────────────────────────

    def _tickets_in_range(self, tickets: List[Ticket], start: datetime, end: datetime) -> List[Ticket]:
        """Return tickets created within [start, end]."""
        result = []
        for t in tickets:
            try:
                created = parse_datetime(t.created_at)
                if start <= created <= end:
                    result.append(t)
            except ValueError:
                pass
        return result

    # ── Daily Report ──────────────────────────────────────────

    @timer
    @audit_log("Generate Daily Report")
    def daily_report(self, date: Optional[datetime] = None) -> dict:
        """
        Generate a report for a specific day (defaults to today).
        Returns the report as a dictionary and prints it to stdout.
        """
        if date is None:
            date = datetime.now()

        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        all_tickets = self._tm.get_all_tickets()
        day_tickets = self._tickets_in_range(all_tickets, start, end)

        total      = len(day_tickets)
        open_t     = [t for t in day_tickets if t.status == "Open"]
        closed_t   = [t for t in day_tickets if t.status in ("Resolved", "Closed")]
        inprog_t   = [t for t in day_tickets if t.status == "In Progress"]
        escalated  = [t for t in day_tickets if t.status == "Escalated"]
        high_prio  = [t for t in day_tickets if t.priority in ("P1", "P2")]
        breached   = [t for t in day_tickets if t.is_sla_breached()]
        by_priority = count_by_priority(day_tickets)  # type: ignore[arg-type]

        report = {
            "report_type":       "Daily",
            "date":              date.strftime("%Y-%m-%d"),
            "generated_at":      now_str(),
            "total_tickets":     total,
            "open_tickets":      len(open_t),
            "in_progress":       len(inprog_t),
            "closed_tickets":    len(closed_t),
            "escalated_tickets": len(escalated),
            "high_priority":     len(high_prio),
            "sla_breaches":      len(breached),
            "by_priority":       by_priority,
            "breached_ids":      [t.ticket_id for t in breached],
        }

        self._print_daily_report(report)
        self._save_report(report, f"daily_{date.strftime('%Y%m%d')}.json")
        log.info("[REPORT] Daily report generated for %s", date.strftime("%Y-%m-%d"))
        return report

    def _print_daily_report(self, r: dict) -> None:
        print("\n" + center_banner(f"  DAILY REPORT — {r['date']}  "))
        print(f"  Generated At     : {r['generated_at']}")
        print(f"  Total Tickets    : {r['total_tickets']}")
        print(f"  Open             : {r['open_tickets']}")
        print(f"  In Progress      : {r['in_progress']}")
        print(f"  Closed/Resolved  : {r['closed_tickets']}")
        print(f"  Escalated        : {r['escalated_tickets']}")
        print(f"  High Priority    : {r['high_priority']}  (P1+P2)")
        print(f"  SLA Breaches     : {r['sla_breaches']}")
        print()
        print("  Priority Breakdown:")
        for p in ("P1", "P2", "P3", "P4"):
            count = r["by_priority"].get(p, 0)
            bar = "█" * min(count, 40)
            print(f"    {p}: {bar} {count}")
        if r["breached_ids"]:
            print(f"\n  Breached IDs: {', '.join(r['breached_ids'])}")
        print("=" * 70)

    # ── Monthly Report ────────────────────────────────────────

    @timer
    @audit_log("Generate Monthly Report")
    def monthly_report(self, year: Optional[int] = None, month: Optional[int] = None) -> dict:
        """
        Generate a report for a full calendar month.
        Returns the report dictionary and prints it.
        """
        now = datetime.now()
        year  = year  or now.year
        month = month or now.month

        start = datetime(year, month, 1)
        # Last day of month
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        all_tickets  = self._tm.get_all_tickets()
        month_tickets = self._tickets_in_range(all_tickets, start, end)

        # Most common issue category
        categories = [t.category for t in month_tickets]
        most_common_cat = Counter(categories).most_common(1)[0][0] if categories else "N/A"
        most_common_count = Counter(categories).most_common(1)[0][1] if categories else 0

        # Average resolution time
        avg_resolution = average_resolution_hours(
            [t.to_dict() for t in month_tickets]
        )

        # Department breakdown
        dept_counter = Counter(t.department for t in month_tickets)
        busiest_dept = dept_counter.most_common(1)[0][0] if dept_counter else "N/A"
        busiest_count = dept_counter.most_common(1)[0][1] if dept_counter else 0

        # Repeated problems (categories appearing ≥ 3 times)
        repeated = {cat: cnt for cat, cnt in Counter(categories).items() if cnt >= 3}

        # SLA breaches
        breached = [t for t in month_tickets if t.is_sla_breached()]

        by_priority = count_by_priority(month_tickets)  # type: ignore[arg-type]

        report = {
            "report_type":          "Monthly",
            "period":               f"{year}-{month:02d}",
            "generated_at":         now_str(),
            "total_tickets":        len(month_tickets),
            "open_tickets":         len([t for t in month_tickets if t.status == "Open"]),
            "closed_tickets":       len([t for t in month_tickets if t.status in ("Resolved", "Closed")]),
            "high_priority":        len([t for t in month_tickets if t.priority in ("P1", "P2")]),
            "sla_breaches":         len(breached),
            "by_priority":          by_priority,
            "most_common_issue":    most_common_cat,
            "most_common_count":    most_common_count,
            "avg_resolution_hours": avg_resolution,
            "busiest_department":   busiest_dept,
            "busiest_dept_count":   busiest_count,
            "department_breakdown": dict(dept_counter),
            "repeated_problems":    repeated,
        }

        self._print_monthly_report(report)
        self._save_report(report, f"monthly_{year}{month:02d}.json")
        self._export_monthly_csv(month_tickets, year, month)
        log.info("[REPORT] Monthly report generated for %s-%02d", year, month)
        return report

    def _print_monthly_report(self, r: dict) -> None:
        print("\n" + center_banner(f"  MONTHLY REPORT — {r['period']}  "))
        print(f"  Generated At          : {r['generated_at']}")
        print(f"  Total Tickets         : {r['total_tickets']}")
        print(f"  Open                  : {r['open_tickets']}")
        print(f"  Closed/Resolved       : {r['closed_tickets']}")
        print(f"  High Priority         : {r['high_priority']}")
        print(f"  SLA Breaches          : {r['sla_breaches']}")
        print(f"  Most Common Issue     : {r['most_common_issue']} ({r['most_common_count']} tickets)")
        print(f"  Avg Resolution Time   : {r['avg_resolution_hours']:.1f} hours")
        print(f"  Busiest Department    : {r['busiest_department']} ({r['busiest_dept_count']} tickets)")
        print()
        print("  Department Breakdown:")
        for dept, cnt in sorted(r["department_breakdown"].items(), key=lambda x: -x[1]):
            bar = "█" * min(cnt, 30)
            print(f"    {dept:<25} {bar} {cnt}")
        if r["repeated_problems"]:
            print("\n  Repeated Problems (≥3 occurrences):")
            for cat, cnt in sorted(r["repeated_problems"].items(), key=lambda x: -x[1]):
                print(f"    {cat:<35} {cnt} tickets")
        print("=" * 70)

    # ── Persistence ───────────────────────────────────────────

    def _save_report(self, report: dict, filename: str) -> None:
        """Save a report dictionary to a JSON file in the reports directory."""
        path = os.path.join(REPORTS_DIR, filename)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, ensure_ascii=False)
            log.info("Report saved: %s", path)
        except OSError as exc:
            log.error("Could not save report %s: %s", filename, exc)

    def _export_monthly_csv(self, tickets: List[Ticket], year: int, month: int) -> None:
        """Export all month tickets to a per-month CSV file."""
        path = os.path.join(REPORTS_DIR, f"monthly_{year}{month:02d}_tickets.csv")
        fieldnames = [
            "ticket_id", "ticket_type", "employee_name", "department",
            "category", "priority", "status", "created_at", "resolved_at",
        ]
        try:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for t in tickets:
                    writer.writerow(t.to_dict())
            log.info("Monthly CSV exported: %s", path)
        except OSError as exc:
            log.error("CSV export failed: %s", exc)

    # ── Quick summary (for main menu) ─────────────────────────

    def quick_summary(self) -> None:
        """Print a one-line summary of key metrics."""
        stats = self._tm.summary_stats()
        print(
            f"  Total: {stats['total']}  |  Open: {stats['open']}  |  "
            f"Closed: {stats['closed']}  |  High-Priority: {stats['high_priority']}  |  "
            f"SLA Breached: {stats['sla_breached']}"
        )
