"""
itil.py - ITIL Process Management Module
Automated ITIL Service Desk System

Implements ITIL best-practice workflows:
  ─ IncidentManager   : log, categorise, escalate, resolve incidents
  ─ ProblemManager    : detect recurring issues, create Problem Records
  ─ ChangeManager     : request, approve, implement, verify changes
  ─ SLAManager        : track SLA compliance across all tickets
"""

import json
import os
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from logger import get_logger
from tickets import (
    IncidentTicket,
    ProblemRecord,
    ServiceRequest,
    Ticket,
    TicketManager,
    ticket_from_dict,
)
from utils import (
    SLA_HOURS,
    EmptyFieldError,
    SLABreachError,
    TicketNotFoundError,
    audit_log,
    now_str,
    parse_datetime,
    timer,
    validate_non_empty,
    validate_priority,
    validate_status,
)

log = get_logger("itil")

DATA_DIR      = os.path.join(os.path.dirname(__file__), "data")
PROBLEMS_FILE = os.path.join(DATA_DIR, "problems.json")

os.makedirs(DATA_DIR, exist_ok=True)

# Threshold: number of same-category incidents before a Problem Record is raised
PROBLEM_THRESHOLD = 5


# ═══════════════════════════════════════════════════════════════
# Incident Manager
# ═══════════════════════════════════════════════════════════════

class IncidentManager:
    """
    ITIL Incident Management workflow.
    Handles the lifecycle: Log → Categorise → Prioritise → Escalate → Resolve.
    """

    def __init__(self, ticket_manager: TicketManager):
        self._tm = ticket_manager

    @audit_log("Log Incident")
    def log_incident(
        self,
        employee_name: str,
        department: str,
        issue_description: str,
        category: str,
        priority: Optional[str] = None,
        impact: str = "Medium",
        urgency: str = "Medium",
        workaround: str = "",
    ) -> IncidentTicket:
        """
        Create a new IncidentTicket and log it.
        Priority is auto-detected if not provided.
        """
        ticket = self._tm.create_ticket(
            employee_name     = employee_name,
            department        = department,
            issue_description = issue_description,
            category          = category,
            ticket_type       = "IncidentTicket",
            priority          = priority,
            impact            = impact,
            urgency           = urgency,
            workaround        = workaround,
        )
        log.info("[INCIDENT] Logged: %s | Priority: %s", ticket.ticket_id, ticket.priority)
        return ticket  # type: ignore[return-value]

    def categorise(self, ticket_id: str, category: str) -> None:
        """Update the category of an existing incident (if re-classification needed)."""
        # Category is immutable in the current model; we log it as an update note
        ticket = self._tm.get_ticket(ticket_id)
        log.info("[INCIDENT] Re-categorised %s → %s", ticket_id, category)

    def escalate(self, ticket_id: str) -> Ticket:
        """Escalate an incident to the next support tier."""
        ticket = self._tm.escalate_ticket(ticket_id)
        log.warning("[INCIDENT] Escalated: %s", ticket_id)
        return ticket

    def resolve(self, ticket_id: str, resolution_note: str = "") -> Ticket:
        """Mark an incident as Resolved."""
        ticket = self._tm.update_status(ticket_id, "Resolved")
        log.info("[INCIDENT] Resolved: %s — %s", ticket_id, resolution_note or "No note.")
        return ticket

    def get_open_incidents(self) -> List[IncidentTicket]:
        """Return all open or in-progress incidents."""
        return [
            t for t in self._tm.get_all_tickets()
            if isinstance(t, IncidentTicket) and t.status in ("Open", "In Progress", "Escalated")
        ]

    def check_and_escalate_sla(self) -> List[Ticket]:
        """Auto-escalate any breached SLA incidents and return the list."""
        escalated = self._tm.escalate_breached_tickets()
        for t in escalated:
            log.warning("[INCIDENT][SLA] Auto-escalated: %s (%s)", t.ticket_id, t.priority)
        return escalated


# ═══════════════════════════════════════════════════════════════
# Problem Manager
# ═══════════════════════════════════════════════════════════════

class ProblemManager:
    """
    ITIL Problem Management workflow.
    Monitors recurring incidents and raises Problem Records after PROBLEM_THRESHOLD.
    Persists problem records to problems.json.
    """

    def __init__(self, ticket_manager: TicketManager):
        self._tm = ticket_manager
        self._problems: Dict[str, ProblemRecord] = {}
        self._load_problems()

    # ── Persistence ───────────────────────────────────────────

    def _load_problems(self) -> None:
        if not os.path.exists(PROBLEMS_FILE):
            return
        try:
            with open(PROBLEMS_FILE, "r", encoding="utf-8") as fh:
                data: List[dict] = json.load(fh)
            for d in data:
                pr = ProblemRecord.from_dict(d)
                self._problems[pr.ticket_id] = pr
            log.info("Loaded %d problem record(s).", len(self._problems))
        except (json.JSONDecodeError, KeyError) as exc:
            log.error("Failed to load problems.json: %s", exc)

    def _save_problems(self) -> None:
        try:
            with open(PROBLEMS_FILE, "w", encoding="utf-8") as fh:
                json.dump([p.to_dict() for p in self._problems.values()], fh, indent=2, ensure_ascii=False)
            log.info("Saved %d problem record(s).", len(self._problems))
        except OSError as exc:
            log.error("Could not save problems.json: %s", exc)

    # ── Core Logic ────────────────────────────────────────────

    def analyse_recurring_issues(self) -> List[ProblemRecord]:
        """
        Scan all incident tickets for categories appearing >= PROBLEM_THRESHOLD times.
        Auto-create a ProblemRecord for each newly detected pattern.
        Returns the list of newly created Problem Records.
        """
        incidents = [t for t in self._tm.get_all_tickets() if isinstance(t, IncidentTicket)]
        category_counter = Counter(t.category for t in incidents)
        existing_categories = {pr.category for pr in self._problems.values()}

        new_problems: List[ProblemRecord] = []

        for category, count in category_counter.items():
            if count >= PROBLEM_THRESHOLD and category not in existing_categories:
                related_ids = [t.ticket_id for t in incidents if t.category == category]
                pr = self._create_problem_record(
                    category        = category,
                    related_incidents = related_ids,
                    occurrence_count  = count,
                )
                new_problems.append(pr)
                log.warning(
                    "[PROBLEM] Recurring issue detected in category '%s' (%d occurrences). "
                    "Problem Record created: %s",
                    category, count, pr.ticket_id,
                )

        return new_problems

    @audit_log("Create Problem Record")
    def _create_problem_record(
        self,
        category: str,
        related_incidents: List[str],
        occurrence_count: int,
    ) -> ProblemRecord:
        """Create and persist a new ProblemRecord."""
        pr = ProblemRecord(
            employee_name     = "Problem Management",
            department        = "IT Operations",
            issue_description = (
                f"Recurring issue detected in category '{category}' "
                f"({occurrence_count} occurrences). Root cause under investigation."
            ),
            category          = category,
            priority          = "P2",
            related_incidents = related_incidents,
            root_cause        = "Under Investigation",
            known_error       = False,
        )
        self._problems[pr.ticket_id] = pr
        self._save_problems()
        return pr

    def update_root_cause(self, problem_id: str, root_cause: str, known_error: bool = False) -> ProblemRecord:
        """Update the root cause of a Problem Record."""
        if problem_id not in self._problems:
            raise TicketNotFoundError(f"Problem Record '{problem_id}' not found.")
        pr = self._problems[problem_id]
        pr.root_cause = root_cause
        pr._known_error = known_error
        self._save_problems()
        log.info("[PROBLEM] Root cause updated for %s: %s", problem_id, root_cause)
        return pr

    def get_all_problems(self) -> List[ProblemRecord]:
        """Return all Problem Records."""
        return list(self._problems.values())


# ═══════════════════════════════════════════════════════════════
# Change Manager
# ═══════════════════════════════════════════════════════════════

class ChangeRecord:
    """Lightweight Change Record (no Ticket base — different lifecycle)."""

    def __init__(
        self,
        change_id: str,
        title: str,
        description: str,
        requested_by: str,
        change_type: str = "Standard",   # Standard | Emergency | Normal
        status: str = "Requested",
        created_at: Optional[str] = None,
    ):
        self.change_id    = change_id
        self.title        = title
        self.description  = description
        self.requested_by = requested_by
        self.change_type  = change_type
        self.status       = status          # Requested | Approved | Implementing | Verified | Closed
        self.created_at   = created_at or now_str()
        self.approved_at: Optional[str] = None
        self.implemented_at: Optional[str] = None
        self.closed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_dict(cls, d: dict) -> "ChangeRecord":
        cr = cls(
            change_id    = d["change_id"],
            title        = d["title"],
            description  = d["description"],
            requested_by = d["requested_by"],
            change_type  = d.get("change_type", "Standard"),
            status       = d.get("status", "Requested"),
            created_at   = d.get("created_at"),
        )
        cr.approved_at     = d.get("approved_at")
        cr.implemented_at  = d.get("implemented_at")
        cr.closed_at       = d.get("closed_at")
        return cr

    def __str__(self) -> str:
        return f"[{self.change_id}] {self.change_type} | {self.status} | {self.title}"


CHANGES_FILE = os.path.join(DATA_DIR, "changes.json")


class ChangeManager:
    """
    ITIL Change Management workflow.
    Lifecycle: Request → Approve → Implement → Verify → Close.
    """

    def __init__(self):
        self._changes: Dict[str, ChangeRecord] = {}
        self._load_changes()

    def _load_changes(self) -> None:
        if not os.path.exists(CHANGES_FILE):
            return
        try:
            with open(CHANGES_FILE, "r", encoding="utf-8") as fh:
                for d in json.load(fh):
                    cr = ChangeRecord.from_dict(d)
                    self._changes[cr.change_id] = cr
            log.info("Loaded %d change record(s).", len(self._changes))
        except (json.JSONDecodeError, KeyError) as exc:
            log.error("Could not load changes.json: %s", exc)

    def _save_changes(self) -> None:
        try:
            with open(CHANGES_FILE, "w", encoding="utf-8") as fh:
                json.dump([c.to_dict() for c in self._changes.values()], fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            log.error("Could not save changes.json: %s", exc)

    @audit_log("Request Change")
    def request_change(
        self,
        title: str,
        description: str,
        requested_by: str,
        change_type: str = "Standard",
    ) -> ChangeRecord:
        """Submit a new Change Request."""
        import uuid
        change_id = "CHG-" + uuid.uuid4().hex[:6].upper()
        cr = ChangeRecord(
            change_id    = change_id,
            title        = title,
            description  = description,
            requested_by = requested_by,
            change_type  = change_type,
        )
        self._changes[change_id] = cr
        self._save_changes()
        log.info("[CHANGE] Requested: %s", cr)
        return cr

    def approve_change(self, change_id: str, approved_by: str) -> ChangeRecord:
        cr = self._get_change(change_id)
        cr.status      = "Approved"
        cr.approved_at = now_str()
        self._save_changes()
        log.info("[CHANGE] Approved: %s by %s", change_id, approved_by)
        return cr

    def implement_change(self, change_id: str) -> ChangeRecord:
        cr = self._get_change(change_id)
        if cr.status != "Approved":
            raise ValueError(f"Change {change_id} is not approved yet (status: {cr.status}).")
        cr.status           = "Implementing"
        cr.implemented_at   = now_str()
        self._save_changes()
        log.info("[CHANGE] Implementation started: %s", change_id)
        return cr

    def verify_change(self, change_id: str) -> ChangeRecord:
        cr = self._get_change(change_id)
        cr.status = "Verified"
        self._save_changes()
        log.info("[CHANGE] Verified: %s", change_id)
        return cr

    def close_change(self, change_id: str) -> ChangeRecord:
        cr = self._get_change(change_id)
        cr.status    = "Closed"
        cr.closed_at = now_str()
        self._save_changes()
        log.info("[CHANGE] Closed: %s", change_id)
        return cr

    def get_all_changes(self) -> List[ChangeRecord]:
        return list(self._changes.values())

    def _get_change(self, change_id: str) -> ChangeRecord:
        if change_id not in self._changes:
            raise TicketNotFoundError(f"Change Record '{change_id}' not found.")
        return self._changes[change_id]


# ═══════════════════════════════════════════════════════════════
# SLA Manager
# ═══════════════════════════════════════════════════════════════

class SLAManager:
    """
    ITIL SLA Management.
    Tracks compliance, generates breach reports, escalates tickets.
    """

    def __init__(self, ticket_manager: TicketManager):
        self._tm = ticket_manager

    def get_sla_report(self) -> dict:
        """
        Return a comprehensive SLA compliance report across all priorities.
        """
        report: Dict[str, dict] = {}
        for priority in ("P1", "P2", "P3", "P4"):
            tickets = self._tm.filter_by_priority(priority)
            total   = len(tickets)
            breached = [t for t in tickets if t.is_sla_breached()]
            compliant = total - len(breached)
            report[priority] = {
                "sla_hours":      SLA_HOURS[priority],
                "total_tickets":  total,
                "compliant":      compliant,
                "breached":       len(breached),
                "breached_ids":   [t.ticket_id for t in breached],
                "compliance_pct": round((compliant / total * 100), 1) if total else 100.0,
            }
        return report

    def display_sla_report(self) -> None:
        """Pretty-print the SLA compliance report."""
        report = self.get_sla_report()
        print("=" * 65)
        print("  SLA COMPLIANCE REPORT")
        print("=" * 65)
        print(f"  {'Priority':<10} {'SLA':>6} {'Total':>7} {'Compliant':>10} {'Breached':>9} {'%':>7}")
        print("-" * 65)
        for p, d in report.items():
            print(
                f"  {p:<10} {d['sla_hours']:>4}h {d['total_tickets']:>7} "
                f"{d['compliant']:>10} {d['breached']:>9} {d['compliance_pct']:>6.1f}%"
            )
        print("=" * 65)

    @audit_log("Escalate Breached SLAs")
    def escalate_breached(self) -> List[Ticket]:
        """Escalate all breached SLA tickets and log warnings."""
        breached_all = []
        for p in ("P1", "P2", "P3", "P4"):
            tickets = self._tm.filter_by_priority(p)
            for t in tickets:
                if t.is_sla_breached() and t.status not in ("Escalated", "Resolved", "Closed"):
                    self._tm.escalate_ticket(t.ticket_id)
                    log.warning("[SLA] Breached & escalated: %s (%s)", t.ticket_id, p)
                    breached_all.append(t)
        return breached_all

    def generate_warnings(self) -> List[str]:
        """
        Generate textual SLA warnings for tickets nearing breach (< 1h remaining).
        """
        warnings = []
        for t in self._tm.get_all_tickets():
            if t.status in ("Open", "In Progress"):
                remaining = t.sla_remaining_hours()
                if 0 < remaining < 1.0:
                    msg = (
                        f"WARNING: Ticket {t.ticket_id} ({t.priority}) has only "
                        f"{remaining:.1f}h before SLA breach!"
                    )
                    warnings.append(msg)
                    log.warning("[SLA] %s", msg)
        return warnings
