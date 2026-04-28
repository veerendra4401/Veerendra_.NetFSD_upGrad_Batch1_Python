"""
tickets.py - Ticket Management Module
Automated ITIL Service Desk System

OOP Classes:
  Ticket            – base class (Encapsulation, Special Methods)
  IncidentTicket    – inherits Ticket (Inheritance, Polymorphism)
  ServiceRequest    – inherits Ticket
  ProblemRecord     – inherits Ticket
  TicketManager     – CRUD operations, JSON persistence, SLA tracking
"""

import csv
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from logger import get_logger
from utils import (
    DuplicateTicketError,
    EmptyFieldError,
    FileOperationError,
    SLABreachError,
    TicketNotFoundError,
    audit_log,
    detect_priority,
    generate_ticket_id,
    now_str,
    parse_datetime,
    timer,
    truncate,
    validate_non_empty,
    validate_priority,
    validate_status,
    SLA_HOURS,
    VALID_STATUSES,
)

log = get_logger("tickets")

DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.json")
BACKUP_FILE  = os.path.join(DATA_DIR, "backup.csv")

os.makedirs(DATA_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# Base Ticket Class
# ═══════════════════════════════════════════════════════════════

class Ticket:
    """
    Base ticket class demonstrating:
      - Constructor (__init__)
      - Encapsulation (private _ticket_id)
      - Instance Variables
      - Special Methods (__str__, __repr__, __eq__, __hash__)
      - Static Methods
      - Properties
    """

    _ticket_counter: int = 0   # class variable (shared state)

    def __init__(
        self,
        employee_name: str,
        department: str,
        issue_description: str,
        category: str,
        priority: Optional[str] = None,
        ticket_id: Optional[str] = None,
        status: str = "Open",
        created_at: Optional[str] = None,
        resolved_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        # ── Validation ────────────────────────────────────────
        self._employee_name    = validate_non_empty(employee_name, "employee_name")
        self._department       = validate_non_empty(department, "department")
        self._issue_description = validate_non_empty(issue_description, "issue_description")
        self._category         = validate_non_empty(category, "category")

        # ── Auto-detect priority from description if not supplied ──
        self._priority = validate_priority(priority) if priority else detect_priority(issue_description)

        # ── ID & Timestamps ───────────────────────────────────
        self._ticket_id  = ticket_id if ticket_id else generate_ticket_id()
        self._status     = validate_status(status)
        self._created_at = created_at if created_at else now_str()
        self._resolved_at = resolved_at
        self._updated_at  = updated_at if updated_at else self._created_at

        Ticket._ticket_counter += 1

    # ── Properties (Encapsulation) ────────────────────────────

    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def employee_name(self) -> str:
        return self._employee_name

    @property
    def department(self) -> str:
        return self._department

    @property
    def issue_description(self) -> str:
        return self._issue_description

    @property
    def category(self) -> str:
        return self._category

    @property
    def priority(self) -> str:
        return self._priority

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str):
        self._status = validate_status(new_status)
        self._updated_at = now_str()

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def resolved_at(self) -> Optional[str]:
        return self._resolved_at

    @resolved_at.setter
    def resolved_at(self, value: str):
        self._resolved_at = value

    @property
    def updated_at(self) -> str:
        return self._updated_at

    # ── Special Methods ───────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"[{self._ticket_id}] {self._priority} | {self._status} | "
            f"{self._employee_name} ({self._department}) — {truncate(self._issue_description)}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(ticket_id={self._ticket_id!r}, "
            f"priority={self._priority!r}, status={self._status!r})"
        )

    def __eq__(self, other) -> bool:
        return isinstance(other, Ticket) and self._ticket_id == other._ticket_id

    def __hash__(self) -> int:
        return hash(self._ticket_id)

    # ── Static Methods ────────────────────────────────────────

    @staticmethod
    def get_sla_deadline(priority: str, created_at: str) -> datetime:
        """Return the SLA deadline datetime for a given priority and creation time."""
        hours = SLA_HOURS.get(priority, 24)
        return parse_datetime(created_at) + timedelta(hours=hours)

    @staticmethod
    def total_created() -> int:
        """Return total number of Ticket objects instantiated this session."""
        return Ticket._ticket_counter

    # ── Serialisation ─────────────────────────────────────────

    def to_dict(self) -> dict:
        """Convert ticket to a plain dictionary (for JSON storage)."""
        return {
            "ticket_type":        self.__class__.__name__,
            "ticket_id":          self._ticket_id,
            "employee_name":      self._employee_name,
            "department":         self._department,
            "issue_description":  self._issue_description,
            "category":           self._category,
            "priority":           self._priority,
            "status":             self._status,
            "created_at":         self._created_at,
            "resolved_at":        self._resolved_at,
            "updated_at":         self._updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Ticket":
        """Reconstruct a Ticket from a dictionary (used on load)."""
        return cls(
            employee_name     = data["employee_name"],
            department        = data["department"],
            issue_description = data["issue_description"],
            category          = data["category"],
            priority          = data["priority"],
            ticket_id         = data["ticket_id"],
            status            = data["status"],
            created_at        = data.get("created_at"),
            resolved_at       = data.get("resolved_at"),
            updated_at        = data.get("updated_at"),
        )

    # ── SLA helpers ───────────────────────────────────────────

    def is_sla_breached(self) -> bool:
        """Return True if the SLA deadline has passed and ticket is still open."""
        if self._status in ("Resolved", "Closed"):
            return False
        deadline = Ticket.get_sla_deadline(self._priority, self._created_at)
        return datetime.now() > deadline

    def sla_remaining_hours(self) -> float:
        """Return hours remaining until SLA breach (negative = already breached)."""
        deadline = Ticket.get_sla_deadline(self._priority, self._created_at)
        delta = deadline - datetime.now()
        return round(delta.total_seconds() / 3600, 2)

    # ── Polymorphic method ────────────────────────────────────

    def ticket_type_label(self) -> str:
        """Return a human-readable ticket type label (overridden in subclasses)."""
        return "General Ticket"


# ═══════════════════════════════════════════════════════════════
# Subclass: IncidentTicket
# ═══════════════════════════════════════════════════════════════

class IncidentTicket(Ticket):
    """
    Represents an ITIL Incident — an unplanned service disruption.
    Adds: impact, urgency, workaround.
    Demonstrates Inheritance & Polymorphism.
    """

    def __init__(self, *args, impact: str = "Medium", urgency: str = "Medium",
                 workaround: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._impact     = impact
        self._urgency    = urgency
        self._workaround = workaround

    @property
    def impact(self) -> str:
        return self._impact

    @property
    def urgency(self) -> str:
        return self._urgency

    @property
    def workaround(self) -> str:
        return self._workaround

    def ticket_type_label(self) -> str:   # Polymorphism
        return "Incident"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"impact": self._impact, "urgency": self._urgency, "workaround": self._workaround})
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "IncidentTicket":
        return cls(
            employee_name     = data["employee_name"],
            department        = data["department"],
            issue_description = data["issue_description"],
            category          = data["category"],
            priority          = data["priority"],
            ticket_id         = data["ticket_id"],
            status            = data["status"],
            created_at        = data.get("created_at"),
            resolved_at       = data.get("resolved_at"),
            updated_at        = data.get("updated_at"),
            impact            = data.get("impact", "Medium"),
            urgency           = data.get("urgency", "Medium"),
            workaround        = data.get("workaround", ""),
        )


# ═══════════════════════════════════════════════════════════════
# Subclass: ServiceRequest
# ═══════════════════════════════════════════════════════════════

class ServiceRequest(Ticket):
    """
    Represents an ITIL Service Request — a standard, pre-approved request.
    Adds: requested_service, approved_by.
    """

    def __init__(self, *args, requested_service: str = "", approved_by: str = "Pending", **kwargs):
        super().__init__(*args, **kwargs)
        self._requested_service = requested_service
        self._approved_by       = approved_by

    @property
    def requested_service(self) -> str:
        return self._requested_service

    @property
    def approved_by(self) -> str:
        return self._approved_by

    def ticket_type_label(self) -> str:
        return "Service Request"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"requested_service": self._requested_service, "approved_by": self._approved_by})
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ServiceRequest":
        return cls(
            employee_name     = data["employee_name"],
            department        = data["department"],
            issue_description = data["issue_description"],
            category          = data["category"],
            priority          = data["priority"],
            ticket_id         = data["ticket_id"],
            status            = data["status"],
            created_at        = data.get("created_at"),
            resolved_at       = data.get("resolved_at"),
            updated_at        = data.get("updated_at"),
            requested_service = data.get("requested_service", ""),
            approved_by       = data.get("approved_by", "Pending"),
        )


# ═══════════════════════════════════════════════════════════════
# Subclass: ProblemRecord
# ═══════════════════════════════════════════════════════════════

class ProblemRecord(Ticket):
    """
    Represents an ITIL Problem — root-cause of recurring incidents.
    Adds: root_cause, related_incidents, known_error.
    """

    def __init__(self, *args, root_cause: str = "Under Investigation",
                 related_incidents: Optional[List[str]] = None,
                 known_error: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self._root_cause         = root_cause
        self._related_incidents  = related_incidents or []
        self._known_error        = known_error

    @property
    def root_cause(self) -> str:
        return self._root_cause

    @root_cause.setter
    def root_cause(self, value: str):
        self._root_cause = value

    @property
    def related_incidents(self) -> List[str]:
        return self._related_incidents

    @property
    def known_error(self) -> bool:
        return self._known_error

    def ticket_type_label(self) -> str:
        return "Problem Record"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "root_cause":        self._root_cause,
            "related_incidents": self._related_incidents,
            "known_error":       self._known_error,
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ProblemRecord":
        return cls(
            employee_name     = data["employee_name"],
            department        = data["department"],
            issue_description = data["issue_description"],
            category          = data["category"],
            priority          = data["priority"],
            ticket_id         = data["ticket_id"],
            status            = data["status"],
            created_at        = data.get("created_at"),
            resolved_at       = data.get("resolved_at"),
            updated_at        = data.get("updated_at"),
            root_cause        = data.get("root_cause", "Under Investigation"),
            related_incidents = data.get("related_incidents", []),
            known_error       = data.get("known_error", False),
        )


# ═══════════════════════════════════════════════════════════════
# Factory function
# ═══════════════════════════════════════════════════════════════

_TICKET_TYPE_MAP = {
    "IncidentTicket": IncidentTicket,
    "ServiceRequest":  ServiceRequest,
    "ProblemRecord":   ProblemRecord,
    "Ticket":          Ticket,
}


def ticket_from_dict(data: dict) -> Ticket:
    """Factory: reconstruct the correct Ticket subclass from a dictionary."""
    cls = _TICKET_TYPE_MAP.get(data.get("ticket_type", "Ticket"), Ticket)
    return cls.from_dict(data)


# ═══════════════════════════════════════════════════════════════
# TicketManager — CRUD + Persistence
# ═══════════════════════════════════════════════════════════════

class TicketManager:
    """
    Central manager for all ticket operations.
    Handles: Create, Read, Update, Delete, Search, Sort, SLA tracking, Backup.
    Data is persisted to tickets.json and backed up to backup.csv.
    """

    def __init__(self):
        self._tickets: Dict[str, Ticket] = {}
        self._load_tickets()
        log.info("TicketManager initialised — %d ticket(s) loaded.", len(self._tickets))

    # ── Persistence ───────────────────────────────────────────

    def _load_tickets(self) -> None:
        """Load tickets from JSON file at startup."""
        if not os.path.exists(TICKETS_FILE):
            log.info("No existing tickets.json found; starting fresh.")
            return
        try:
            with open(TICKETS_FILE, "r", encoding="utf-8") as fh:
                raw: List[dict] = json.load(fh)
            for record in raw:
                t = ticket_from_dict(record)
                self._tickets[t.ticket_id] = t
            log.info("Loaded %d tickets from %s", len(self._tickets), TICKETS_FILE)
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            log.error("Failed to load tickets.json: %s", exc)
            raise FileOperationError(f"Could not parse tickets.json: {exc}") from exc

    @timer
    @audit_log("Save Tickets")
    def _save_tickets(self) -> None:
        """Persist all tickets to tickets.json."""
        try:
            data = [t.to_dict() for t in self._tickets.values()]
            with open(TICKETS_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            log.info("Saved %d ticket(s) to %s", len(data), TICKETS_FILE)
        except OSError as exc:
            log.error("Failed to write tickets.json: %s", exc)
            raise FileOperationError(f"Could not save tickets.json: {exc}") from exc

    @timer
    @audit_log("Backup to CSV")
    def backup_to_csv(self) -> None:
        """Export all tickets to backup.csv."""
        if not self._tickets:
            log.warning("No tickets to back up.")
            return
        fieldnames = [
            "ticket_id", "ticket_type", "employee_name", "department",
            "issue_description", "category", "priority", "status",
            "created_at", "resolved_at", "updated_at",
        ]
        try:
            with open(BACKUP_FILE, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for t in self._tickets.values():
                    writer.writerow(t.to_dict())
            log.info("Backup written to %s (%d rows)", BACKUP_FILE, len(self._tickets))
        except OSError as exc:
            log.error("CSV backup failed: %s", exc)
            raise FileOperationError(f"CSV backup failed: {exc}") from exc

    # ── CREATE ────────────────────────────────────────────────

    @audit_log("Create Ticket")
    def create_ticket(
        self,
        employee_name: str,
        department: str,
        issue_description: str,
        category: str,
        ticket_type: str = "IncidentTicket",
        priority: Optional[str] = None,
        **extra,
    ) -> Ticket:
        """
        Create a new ticket of the specified type.
        Auto-detects priority if not provided.
        Raises DuplicateTicketError if the generated ID already exists (extremely unlikely).
        """
        cls = _TICKET_TYPE_MAP.get(ticket_type, IncidentTicket)
        ticket = cls(
            employee_name     = employee_name,
            department        = department,
            issue_description = issue_description,
            category          = category,
            priority          = priority,
            **extra,
        )
        if ticket.ticket_id in self._tickets:
            raise DuplicateTicketError(f"Ticket ID {ticket.ticket_id} already exists.")

        self._tickets[ticket.ticket_id] = ticket
        self._save_tickets()
        log.info("Ticket CREATED: %s", ticket)
        return ticket

    # ── READ ──────────────────────────────────────────────────

    def get_ticket(self, ticket_id: str) -> Ticket:
        """Retrieve a single ticket by ID. Raises TicketNotFoundError if missing."""
        ticket_id = ticket_id.strip().upper()
        if ticket_id not in self._tickets:
            raise TicketNotFoundError(f"Ticket '{ticket_id}' not found.")
        return self._tickets[ticket_id]

    def get_all_tickets(self) -> List[Ticket]:
        """Return all tickets as a list, sorted by creation date descending."""
        return sorted(self._tickets.values(), key=lambda t: t.created_at, reverse=True)

    def search_tickets(self, keyword: str) -> List[Ticket]:
        """
        Full-text search across ticket_id, employee_name, department,
        issue_description, and category.
        """
        kw = keyword.strip().lower()
        results = [
            t for t in self._tickets.values()
            if kw in t.ticket_id.lower()
            or kw in t.employee_name.lower()
            or kw in t.department.lower()
            or kw in t.issue_description.lower()
            or kw in t.category.lower()
        ]
        log.info("Search '%s' → %d result(s)", keyword, len(results))
        return results

    def filter_by_status(self, status: str) -> List[Ticket]:
        """Return tickets matching a specific status."""
        status = validate_status(status)
        return [t for t in self._tickets.values() if t.status == status]

    def filter_by_priority(self, priority: str) -> List[Ticket]:
        """Return tickets matching a specific priority."""
        priority = validate_priority(priority)
        return [t for t in self._tickets.values() if t.priority == priority]

    # ── UPDATE ────────────────────────────────────────────────

    @audit_log("Update Ticket Status")
    def update_status(self, ticket_id: str, new_status: str) -> Ticket:
        """Update a ticket's status. Marks resolved_at when closed/resolved."""
        ticket = self.get_ticket(ticket_id)
        old_status = ticket.status
        ticket.status = new_status
        if new_status in ("Resolved", "Closed") and not ticket.resolved_at:
            ticket.resolved_at = now_str()
        self._save_tickets()
        log.info("Ticket %s status: %s → %s", ticket_id, old_status, new_status)
        return ticket

    @audit_log("Escalate Ticket")
    def escalate_ticket(self, ticket_id: str) -> Ticket:
        """Mark ticket as Escalated (called automatically on SLA breach)."""
        ticket = self.get_ticket(ticket_id)
        ticket.status = "Escalated"
        self._save_tickets()
        log.warning("Ticket %s ESCALATED due to SLA breach.", ticket_id)
        return ticket

    # ── DELETE ────────────────────────────────────────────────

    @audit_log("Delete Ticket")
    def delete_ticket(self, ticket_id: str) -> str:
        """Permanently remove a ticket. Returns confirmation message."""
        ticket_id = ticket_id.strip().upper()
        if ticket_id not in self._tickets:
            raise TicketNotFoundError(f"Ticket '{ticket_id}' not found.")
        del self._tickets[ticket_id]
        self._save_tickets()
        log.info("Ticket DELETED: %s", ticket_id)
        return f"Ticket {ticket_id} has been deleted."

    # ── SLA Monitoring ────────────────────────────────────────

    def get_breached_sla_tickets(self) -> List[Ticket]:
        """Return all open tickets whose SLA deadline has passed."""
        return [t for t in self._tickets.values() if t.is_sla_breached()]

    def escalate_breached_tickets(self) -> List[Ticket]:
        """Auto-escalate all SLA-breached tickets and log warnings."""
        breached = self.get_breached_sla_tickets()
        escalated = []
        for t in breached:
            if t.status not in ("Escalated", "Resolved", "Closed"):
                self.escalate_ticket(t.ticket_id)
                log.warning("[SLA BREACH] Ticket %s escalated — priority %s", t.ticket_id, t.priority)
                escalated.append(t)
        return escalated

    # ── Reporting helpers ─────────────────────────────────────

    def summary_stats(self) -> dict:
        """Return a dictionary of key ticket statistics."""
        all_t = list(self._tickets.values())
        open_t = [t for t in all_t if t.status == "Open"]
        closed_t = [t for t in all_t if t.status in ("Resolved", "Closed")]
        high_p = [t for t in all_t if t.priority in ("P1", "P2")]
        breached = self.get_breached_sla_tickets()
        return {
            "total":       len(all_t),
            "open":        len(open_t),
            "closed":      len(closed_t),
            "high_priority": len(high_p),
            "sla_breached":  len(breached),
        }

    def most_common_issue_category(self) -> str:
        """Return the category that appears most often across all tickets."""
        from collections import Counter
        categories = [t.category for t in self._tickets.values()]
        if not categories:
            return "N/A"
        return Counter(categories).most_common(1)[0][0]

    def department_incident_count(self) -> Dict[str, int]:
        """Return a dict mapping each department to its number of tickets."""
        from collections import Counter
        depts = [t.department for t in self._tickets.values()]
        return dict(Counter(depts))

    # ── Rich display ──────────────────────────────────────────

    def display_ticket(self, ticket: Ticket) -> None:
        """Pretty-print a single ticket to stdout."""
        separator = "-" * 70
        print(separator)
        print(f"  Ticket ID   : {ticket.ticket_id}")
        print(f"  Type        : {ticket.ticket_type_label()}")
        print(f"  Employee    : {ticket.employee_name}")
        print(f"  Department  : {ticket.department}")
        print(f"  Category    : {ticket.category}")
        print(f"  Priority    : {ticket.priority}  ({SLA_HOURS.get(ticket.priority, '?')}h SLA)")
        print(f"  Status      : {ticket.status}")
        print(f"  Created     : {ticket.created_at}")
        print(f"  Updated     : {ticket.updated_at}")
        if ticket.resolved_at:
            print(f"  Resolved    : {ticket.resolved_at}")
        print(f"  SLA Status  : {'BREACHED' if ticket.is_sla_breached() else 'OK'}")
        if not ticket.is_sla_breached() and ticket.status not in ("Resolved", "Closed"):
            print(f"  SLA Remaining: {ticket.sla_remaining_hours():.1f}h")
        print(f"  Description : {ticket.issue_description}")
        # Print subclass-specific fields
        if isinstance(ticket, IncidentTicket):
            print(f"  Impact      : {ticket.impact}")
            print(f"  Urgency     : {ticket.urgency}")
            if ticket.workaround:
                print(f"  Workaround  : {ticket.workaround}")
        elif isinstance(ticket, ServiceRequest):
            print(f"  Service     : {ticket.requested_service}")
            print(f"  Approved By : {ticket.approved_by}")
        elif isinstance(ticket, ProblemRecord):
            print(f"  Root Cause  : {ticket.root_cause}")
            print(f"  Known Error : {ticket.known_error}")
            if ticket.related_incidents:
                print(f"  Related IDs : {', '.join(ticket.related_incidents)}")
        print(separator)
