"""
utils.py - Shared Utilities
Automated ITIL Service Desk System

Demonstrates:
  - Decorators (timing, retry, audit-log)
  - Iterators / Generators
  - map / filter / reduce
  - Basic regex
  - String handling helpers
  - Custom exceptions
"""

import functools
import re
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Generator, Iterable, List

from logger import get_logger

log = get_logger("utils")

# ─────────────────────────────────────────────
# Custom Exceptions
# ─────────────────────────────────────────────

class ITILBaseException(Exception):
    """Root exception for all ITIL service-desk errors."""


class TicketNotFoundError(ITILBaseException):
    """Raised when a requested ticket ID does not exist."""


class DuplicateTicketError(ITILBaseException):
    """Raised when a ticket with the same ID is created twice."""


class InvalidPriorityError(ITILBaseException):
    """Raised when an invalid priority level is supplied."""


class InvalidStatusError(ITILBaseException):
    """Raised when an invalid ticket status is supplied."""


class EmptyFieldError(ITILBaseException):
    """Raised when a mandatory field is empty or blank."""


class SLABreachError(ITILBaseException):
    """Raised when an SLA target has been breached."""


class FileOperationError(ITILBaseException):
    """Raised for failures in file read/write operations."""


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}
VALID_STATUSES   = {"Open", "In Progress", "Resolved", "Closed", "Escalated"}

PRIORITY_RULES: list[tuple[str, str]] = [
    # P1 — critical outages (checked first)
    ("server.*down",       "P1"),
    ("network.*down",      "P1"),
    ("database.*down",     "P1"),
    # P2
    ("internet.*down",     "P2"),
    ("connectivity",       "P2"),
    ("email.*not.*work",   "P2"),
    # P3
    ("laptop.*slow",       "P3"),
    ("slow.*laptop",       "P3"),
    ("high.*cpu",          "P3"),
    ("cpu.*high",          "P3"),
    ("disk.*full",         "P3"),
    ("application.*crash", "P3"),
    ("app.*crash",         "P3"),
    ("printer.*fail",      "P3"),
    # P4
    ("password.*reset",    "P4"),
    ("reset.*password",    "P4"),
    ("software.*install",  "P4"),
    ("access.*request",    "P4"),
]

SLA_HOURS: dict[str, int] = {
    "P1": 1,
    "P2": 4,
    "P3": 8,
    "P4": 24,
}

# ─────────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────────

def timer(func: Callable) -> Callable:
    """Decorator: logs execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        log.debug(f"[TIMER] {func.__name__} executed in {elapsed:.4f}s")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 0.5, exceptions=(Exception,)):
    """Decorator factory: retries a function on specified exceptions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    attempt += 1
                    log.warning(f"[RETRY] {func.__name__} attempt {attempt}/{max_attempts} failed: {exc}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise ITILBaseException(f"{func.__name__} failed after {max_attempts} attempts.")
        return wrapper
    return decorator


def audit_log(action: str):
    """Decorator factory: writes an audit entry before/after the function runs."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log.info(f"[AUDIT] Starting '{action}' via {func.__name__}")
            result = func(*args, **kwargs)
            log.info(f"[AUDIT] Completed '{action}' via {func.__name__}")
            return result
        return wrapper
    return decorator


# ─────────────────────────────────────────────
# ID & Timestamp helpers
# ─────────────────────────────────────────────

def generate_ticket_id() -> str:
    """Generate a unique ticket ID in the format TKT-XXXXXXXX."""
    return "TKT-" + uuid.uuid4().hex[:8].upper()


def now_str() -> str:
    """Return the current datetime as an ISO-8601 string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_datetime(dt_str: str) -> datetime:
    """Parse an ISO-8601 datetime string back to a datetime object."""
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


# ─────────────────────────────────────────────
# Validation helpers
# ─────────────────────────────────────────────

def validate_non_empty(value: Any, field_name: str) -> str:
    """Raise EmptyFieldError if value is blank; otherwise return stripped value."""
    if not isinstance(value, str) or not value.strip():
        raise EmptyFieldError(f"Field '{field_name}' must not be empty.")
    return value.strip()


def validate_priority(priority: str) -> str:
    """Raise InvalidPriorityError if priority is not in VALID_PRIORITIES."""
    p = priority.strip().upper()
    if p not in VALID_PRIORITIES:
        raise InvalidPriorityError(f"Priority '{priority}' is invalid. Choose from {VALID_PRIORITIES}.")
    return p


def validate_status(status: str) -> str:
    """Raise InvalidStatusError if status is not in VALID_STATUSES."""
    s = status.strip().title()
    if s not in VALID_STATUSES:
        raise InvalidStatusError(f"Status '{status}' is invalid. Choose from {VALID_STATUSES}.")
    return s


# ─────────────────────────────────────────────
# Priority auto-detection (regex-based)
# ─────────────────────────────────────────────

def detect_priority(description: str) -> str:
    """
    Scan the issue description with regex to auto-assign a priority.
    PRIORITY_RULES is ordered P1 → P4; first match wins.
    Falls back to P4 if no pattern matches.
    """
    desc_lower = description.lower()
    for pattern, priority in PRIORITY_RULES:
        if re.search(pattern, desc_lower):
            return priority
    return "P4"


# ─────────────────────────────────────────────
# Functional helpers (map / filter / reduce)
# ─────────────────────────────────────────────

def filter_tickets_by_status(tickets: List[dict], status: str) -> List[dict]:
    """Return tickets whose status matches (filter)."""
    return list(filter(lambda t: t.get("status") == status, tickets))


def map_ticket_ids(tickets: List[dict]) -> List[str]:
    """Return a list of ticket IDs (map)."""
    return list(map(lambda t: t.get("ticket_id", ""), tickets))


def count_by_priority(tickets) -> dict:
    """Use reduce to count tickets per priority level.
    Accepts both plain dicts and Ticket objects.
    """
    from functools import reduce
    def _get_priority(ticket):
        # Support both Ticket objects (have .priority property) and plain dicts
        if hasattr(ticket, "priority"):
            return ticket.priority
        return ticket.get("priority", "Unknown")

    def reducer(acc: dict, ticket) -> dict:
        p = _get_priority(ticket)
        acc[p] = acc.get(p, 0) + 1
        return acc
    return reduce(reducer, tickets, {})


def average_resolution_hours(tickets: List[dict]) -> float:
    """Calculate average resolution time (in hours) for closed/resolved tickets."""
    resolved = [
        t for t in tickets
        if t.get("status") in ("Resolved", "Closed") and t.get("resolved_at")
    ]
    if not resolved:
        return 0.0
    durations = []
    for t in resolved:
        try:
            created  = parse_datetime(t["created_at"])
            resolved_at = parse_datetime(t["resolved_at"])
            durations.append((resolved_at - created).total_seconds() / 3600)
        except (KeyError, ValueError):
            pass
    return round(sum(durations) / len(durations), 2) if durations else 0.0


# ─────────────────────────────────────────────
# Generator: paginate tickets
# ─────────────────────────────────────────────

def ticket_page_generator(tickets: List[dict], page_size: int = 10) -> Generator[List[dict], None, None]:
    """Yield successive page_size-sized chunks of the ticket list."""
    for i in range(0, len(tickets), page_size):
        yield tickets[i: i + page_size]


# ─────────────────────────────────────────────
# Iterator: SLA priority iterator
# ─────────────────────────────────────────────

class PriorityIterator:
    """
    Iterator that walks through priorities P1→P4 in order.
    Demonstrates the iterator protocol (__iter__ / __next__).
    """
    _PRIORITIES = ["P1", "P2", "P3", "P4"]

    def __init__(self):
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self._index >= len(self._PRIORITIES):
            raise StopIteration
        p = self._PRIORITIES[self._index]
        self._index += 1
        return p


# ─────────────────────────────────────────────
# String helpers
# ─────────────────────────────────────────────

def truncate(text: str, max_len: int = 50) -> str:
    """Truncate a string to max_len characters, appending '…' if needed."""
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


def mask_sensitive(text: str) -> str:
    """Mask potential passwords or tokens in log messages."""
    return re.sub(r"(?i)(password|token|secret)\s*[:=]\s*\S+", r"\1=***", text)


def center_banner(text: str, width: int = 70, char: str = "=") -> str:
    """Return a centred banner string for CLI output."""
    return f" {text} ".center(width, char)
