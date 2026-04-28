"""
tests.py - Comprehensive Test Suite
Automated ITIL Service Desk System

Tests:
  - Ticket creation & validation
  - Priority auto-detection logic
  - SLA breach detection
  - Auto-monitoring ticket creation
  - File read/write (JSON/CSV)
  - Search functionality
  - Exception handling
  - IncidentManager, ProblemManager, ChangeManager, SLAManager
  - ReportGenerator
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Ensure project root is on path when running tests directly
sys.path.insert(0, os.path.dirname(__file__))

from tickets import (
    IncidentTicket,
    ProblemRecord,
    ServiceRequest,
    Ticket,
    TicketManager,
    ticket_from_dict,
)
from utils import (
    DuplicateTicketError,
    EmptyFieldError,
    InvalidPriorityError,
    InvalidStatusError,
    SLA_HOURS,
    TicketNotFoundError,
    count_by_priority,
    detect_priority,
    generate_ticket_id,
    parse_datetime,
    validate_non_empty,
    validate_priority,
    validate_status,
    average_resolution_hours,
    PriorityIterator,
    ticket_page_generator,
    truncate,
    mask_sensitive,
)
from itil import IncidentManager, ProblemManager, ChangeManager, SLAManager
from monitor import Alert, Monitor
from reports import ReportGenerator


# ═══════════════════════════════════════════════════════════════
# Helper: in-memory TicketManager using a temp file
# ═══════════════════════════════════════════════════════════════

class _TmpTicketManager(TicketManager):
    """TicketManager that writes to a temp file (isolated per test)."""

    def __init__(self, tmp_path: str):
        self._tmp_path = tmp_path
        self._tickets = {}
        # Patch the file paths used by the parent class
        import tickets as _tickets_mod
        self._orig_tf = _tickets_mod.TICKETS_FILE
        self._orig_bf = _tickets_mod.BACKUP_FILE
        _tickets_mod.TICKETS_FILE = tmp_path
        _tickets_mod.BACKUP_FILE  = tmp_path.replace(".json", ".csv")

    def teardown(self):
        import tickets as _tickets_mod
        _tickets_mod.TICKETS_FILE = self._orig_tf
        _tickets_mod.BACKUP_FILE  = self._orig_bf


def _make_tm(tmp_dir: str) -> _TmpTicketManager:
    path = os.path.join(tmp_dir, "test_tickets.json")
    return _TmpTicketManager(path)


# ═══════════════════════════════════════════════════════════════
# 1. Ticket Creation Tests
# ═══════════════════════════════════════════════════════════════

class TestTicketCreation(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)

    def tearDown(self):
        self.tm.teardown()

    def test_create_incident_ticket(self):
        """Ticket is created with all required fields."""
        t = self.tm.create_ticket(
            employee_name="Alice",
            department="HR",
            issue_description="Server is down",
            category="Server Down",
            ticket_type="IncidentTicket",
        )
        self.assertIsInstance(t, IncidentTicket)
        self.assertTrue(t.ticket_id.startswith("TKT-"))
        self.assertEqual(t.employee_name, "Alice")
        self.assertEqual(t.department, "HR")
        self.assertEqual(t.status, "Open")

    def test_create_service_request(self):
        """ServiceRequest subclass is created correctly."""
        t = self.tm.create_ticket(
            employee_name="Bob",
            department="Finance",
            issue_description="Please reset my password",
            category="Password Reset",
            ticket_type="ServiceRequest",
            requested_service="Password Reset",
        )
        self.assertIsInstance(t, ServiceRequest)
        self.assertEqual(t.requested_service, "Password Reset")

    def test_empty_employee_name_raises(self):
        """EmptyFieldError raised when employee_name is blank."""
        with self.assertRaises(EmptyFieldError):
            self.tm.create_ticket(
                employee_name="   ",
                department="IT",
                issue_description="Some issue",
                category="General",
            )

    def test_empty_description_raises(self):
        """EmptyFieldError raised when issue_description is blank."""
        with self.assertRaises(EmptyFieldError):
            self.tm.create_ticket(
                employee_name="Charlie",
                department="IT",
                issue_description="",
                category="General",
            )

    def test_invalid_priority_raises(self):
        """InvalidPriorityError raised for invalid priority string."""
        with self.assertRaises(InvalidPriorityError):
            self.tm.create_ticket(
                employee_name="Dave",
                department="IT",
                issue_description="Some issue",
                category="General",
                priority="P9",
            )

    def test_invalid_status_raises(self):
        """InvalidStatusError raised when setting an invalid status."""
        t = self.tm.create_ticket(
            employee_name="Eve",
            department="IT",
            issue_description="Printer failure",
            category="Printer",
        )
        with self.assertRaises(InvalidStatusError):
            t.status = "Pending"

    def test_ticket_id_unique(self):
        """Each ticket receives a unique ID."""
        ids = set()
        for i in range(20):
            t = self.tm.create_ticket(
                employee_name=f"User{i}",
                department="IT",
                issue_description=f"Issue number {i}",
                category="General",
            )
            ids.add(t.ticket_id)
        self.assertEqual(len(ids), 20)

    def test_ticket_equality(self):
        """Two Ticket objects with the same ID are considered equal."""
        t = self.tm.create_ticket(
            employee_name="Frank",
            department="IT",
            issue_description="Laptop slow",
            category="Performance",
        )
        t_copy = ticket_from_dict(t.to_dict())
        self.assertEqual(t, t_copy)


# ═══════════════════════════════════════════════════════════════
# 2. Priority Logic Tests
# ═══════════════════════════════════════════════════════════════

class TestPriorityLogic(unittest.TestCase):

    def test_server_down_is_p1(self):
        self.assertEqual(detect_priority("The server is down"), "P1")

    def test_internet_down_is_p2(self):
        self.assertEqual(detect_priority("Internet down in office"), "P2")

    def test_laptop_slow_is_p3(self):
        self.assertEqual(detect_priority("My laptop slow today"), "P3")

    def test_password_reset_is_p4(self):
        self.assertEqual(detect_priority("I need a password reset"), "P4")

    def test_unknown_issue_defaults_p4(self):
        self.assertEqual(detect_priority("My chair is broken"), "P4")

    def test_case_insensitive_detection(self):
        self.assertEqual(detect_priority("SERVER DOWN ALERT"), "P1")

    def test_validate_priority_uppercase(self):
        self.assertEqual(validate_priority("p1"), "P1")

    def test_validate_priority_invalid(self):
        with self.assertRaises(InvalidPriorityError):
            validate_priority("CRITICAL")


# ═══════════════════════════════════════════════════════════════
# 3. SLA Breach Tests
# ═══════════════════════════════════════════════════════════════

class TestSLABreach(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)

    def tearDown(self):
        self.tm.teardown()

    def _ticket_created_hours_ago(self, hours: float, priority: str = "P1") -> Ticket:
        """Create a ticket backdated by 'hours' hours."""
        t = self.tm.create_ticket(
            employee_name="Test",
            department="IT",
            issue_description="Server is down",
            category="Server Down",
            priority=priority,
        )
        # Manually backdate created_at
        past = datetime.now() - timedelta(hours=hours)
        t._created_at = past.strftime("%Y-%m-%d %H:%M:%S")
        return t

    def test_p1_sla_hours(self):
        """P1 SLA is 1 hour."""
        self.assertEqual(SLA_HOURS["P1"], 1)

    def test_p4_sla_hours(self):
        """P4 SLA is 24 hours."""
        self.assertEqual(SLA_HOURS["P4"], 24)

    def test_sla_not_breached_before_deadline(self):
        """Ticket not breached when created just now."""
        t = self._ticket_created_hours_ago(0.1, priority="P1")
        self.assertFalse(t.is_sla_breached())

    def test_sla_breached_after_deadline(self):
        """P1 ticket created 2 hours ago is breached."""
        t = self._ticket_created_hours_ago(2, priority="P1")
        self.assertTrue(t.is_sla_breached())

    def test_resolved_ticket_not_breached(self):
        """Resolved ticket never counts as breached."""
        t = self._ticket_created_hours_ago(5, priority="P1")
        t.status = "Resolved"
        self.assertFalse(t.is_sla_breached())

    def test_get_breached_sla_tickets(self):
        """TicketManager correctly identifies breached tickets."""
        t1 = self._ticket_created_hours_ago(2, priority="P1")  # breached
        t2 = self._ticket_created_hours_ago(0.1, priority="P4")  # not breached
        # Manually register them
        self.tm._tickets[t1.ticket_id] = t1
        self.tm._tickets[t2.ticket_id] = t2
        breached = self.tm.get_breached_sla_tickets()
        self.assertIn(t1, breached)
        self.assertNotIn(t2, breached)

    def test_escalate_breached_tickets(self):
        """Breached tickets are escalated via escalate_breached_tickets()."""
        t = self._ticket_created_hours_ago(2, priority="P1")
        self.tm._tickets[t.ticket_id] = t
        escalated = self.tm.escalate_breached_tickets()
        self.assertEqual(len(escalated), 1)
        self.assertEqual(self.tm.get_ticket(t.ticket_id).status, "Escalated")


# ═══════════════════════════════════════════════════════════════
# 4. Auto-Monitoring Ticket Creation Tests
# ═══════════════════════════════════════════════════════════════

class TestAutoMonitoring(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)
        self.monitor = Monitor(
            cpu_threshold=50.0,
            ram_threshold=50.0,
            disk_threshold=50.0,
            ticket_manager=self.tm,
        )

    def tearDown(self):
        self.tm.teardown()

    def test_cpu_alert_created(self):
        """CPU above threshold triggers an Alert."""
        snapshot = {"timestamp": "2026-01-01 10:00:00", "cpu_percent": 95.0,
                    "ram_percent": 40.0, "disk_free_pct": 60.0, "network_mb": 10.0}
        alerts = self.monitor.check_thresholds(snapshot)
        cpu_alerts = [a for a in alerts if a.alert_type == "CPU"]
        self.assertTrue(len(cpu_alerts) >= 1)

    def test_ram_alert_created(self):
        """RAM above threshold triggers an Alert."""
        snapshot = {"timestamp": "2026-01-01 10:00:00", "cpu_percent": 20.0,
                    "ram_percent": 97.0, "disk_free_pct": 60.0, "network_mb": 10.0}
        alerts = self.monitor.check_thresholds(snapshot)
        ram_alerts = [a for a in alerts if a.alert_type == "RAM"]
        self.assertTrue(len(ram_alerts) >= 1)

    def test_disk_alert_created(self):
        """Disk free below threshold triggers an Alert."""
        snapshot = {"timestamp": "2026-01-01 10:00:00", "cpu_percent": 20.0,
                    "ram_percent": 40.0, "disk_free_pct": 5.0, "network_mb": 10.0}
        alerts = self.monitor.check_thresholds(snapshot)
        disk_alerts = [a for a in alerts if a.alert_type == "DISK"]
        self.assertTrue(len(disk_alerts) >= 1)

    def test_no_alert_when_normal(self):
        """No alerts when all metrics are below thresholds."""
        snapshot = {"timestamp": "2026-01-01 10:00:00", "cpu_percent": 20.0,
                    "ram_percent": 40.0, "disk_free_pct": 70.0, "network_mb": 10.0}
        alerts = self.monitor.check_thresholds(snapshot)
        self.assertEqual(len(alerts), 0)

    def test_auto_ticket_created_on_alert(self):
        """An incident ticket is auto-created when a threshold is breached."""
        before_count = len(self.tm.get_all_tickets())
        snapshot = {"timestamp": "2026-01-01 10:00:00", "cpu_percent": 99.0,
                    "ram_percent": 40.0, "disk_free_pct": 60.0, "network_mb": 10.0}
        self.monitor.check_thresholds(snapshot)
        after_count = len(self.tm.get_all_tickets())
        self.assertGreater(after_count, before_count)


# ═══════════════════════════════════════════════════════════════
# 5. File Read / Write Tests
# ═══════════════════════════════════════════════════════════════

class TestFileOperations(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)

    def tearDown(self):
        self.tm.teardown()

    def test_tickets_saved_to_json(self):
        """Tickets are persisted to JSON after creation."""
        import tickets as _m
        self.tm.create_ticket(
            employee_name="Grace",
            department="IT",
            issue_description="Disk full",
            category="Storage",
        )
        self.assertTrue(os.path.exists(_m.TICKETS_FILE))
        with open(_m.TICKETS_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(len(data), 1)

    def test_tickets_loaded_from_json(self):
        """Tickets persisted in JSON are reloaded correctly."""
        import tickets as _m
        t = self.tm.create_ticket(
            employee_name="Henry",
            department="Finance",
            issue_description="Application crash",
            category="Software",
        )
        # Create a fresh manager pointing to the same file
        tm2 = _TmpTicketManager(_m.TICKETS_FILE)
        tm2._load_tickets()
        loaded = tm2.get_ticket(t.ticket_id)
        self.assertEqual(loaded.employee_name, "Henry")
        tm2.teardown()

    def test_csv_backup_created(self):
        """backup_to_csv() produces a valid CSV file."""
        import tickets as _m
        self.tm.create_ticket(
            employee_name="Irene",
            department="HR",
            issue_description="Password reset needed",
            category="Access",
        )
        self.tm.backup_to_csv()
        self.assertTrue(os.path.exists(_m.BACKUP_FILE))
        with open(_m.BACKUP_FILE, encoding="utf-8") as fh:
            lines = fh.readlines()
        # Header + 1 data row
        self.assertEqual(len(lines), 2)

    def test_update_and_save(self):
        """Status update is reflected in the JSON file."""
        import tickets as _m
        t = self.tm.create_ticket(
            employee_name="Jack",
            department="IT",
            issue_description="High CPU",
            category="Performance",
        )
        self.tm.update_status(t.ticket_id, "Resolved")
        with open(_m.TICKETS_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        saved = next(d for d in data if d["ticket_id"] == t.ticket_id)
        self.assertEqual(saved["status"], "Resolved")


# ═══════════════════════════════════════════════════════════════
# 6. Search Ticket Tests
# ═══════════════════════════════════════════════════════════════

class TestSearchTickets(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)
        self.tm.create_ticket("Alice", "HR", "Printer failure in HR room", "Printer")
        self.tm.create_ticket("Bob",  "IT", "Server down urgently",        "Server Down")
        self.tm.create_ticket("Carol","Finance","Password reset needed",   "Password Reset")

    def tearDown(self):
        self.tm.teardown()

    def test_search_by_employee_name(self):
        results = self.tm.search_tickets("Alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].employee_name, "Alice")

    def test_search_by_department(self):
        results = self.tm.search_tickets("Finance")
        self.assertEqual(len(results), 1)

    def test_search_by_keyword_in_description(self):
        results = self.tm.search_tickets("server")
        self.assertEqual(len(results), 1)
        self.assertIn("Server", results[0].issue_description)

    def test_search_no_results(self):
        results = self.tm.search_tickets("xyzzy_nonexistent")
        self.assertEqual(results, [])

    def test_get_ticket_by_id(self):
        all_t = self.tm.get_all_tickets()
        t = all_t[0]
        retrieved = self.tm.get_ticket(t.ticket_id)
        self.assertEqual(t, retrieved)

    def test_get_ticket_invalid_id_raises(self):
        with self.assertRaises(TicketNotFoundError):
            self.tm.get_ticket("TKT-XXXXXXXX")


# ═══════════════════════════════════════════════════════════════
# 7. Exception Handling Tests
# ═══════════════════════════════════════════════════════════════

class TestExceptionHandling(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)

    def tearDown(self):
        self.tm.teardown()

    def test_delete_nonexistent_ticket(self):
        with self.assertRaises(TicketNotFoundError):
            self.tm.delete_ticket("TKT-NOTEXIST")

    def test_update_nonexistent_ticket(self):
        with self.assertRaises(TicketNotFoundError):
            self.tm.update_status("TKT-NOTEXIST", "Closed")

    def test_validate_non_empty_raises(self):
        with self.assertRaises(EmptyFieldError):
            validate_non_empty("", "test_field")

    def test_validate_non_empty_spaces_raises(self):
        with self.assertRaises(EmptyFieldError):
            validate_non_empty("   ", "test_field")

    def test_validate_status_invalid(self):
        with self.assertRaises(InvalidStatusError):
            validate_status("Waiting")

    def test_corrupted_json_raises_file_error(self):
        """FileOperationError raised when JSON is corrupted."""
        import tickets as _m
        with open(_m.TICKETS_FILE, "w", encoding="utf-8") as fh:
            fh.write("{not valid json}")
        from utils import FileOperationError
        tm2 = _TmpTicketManager(_m.TICKETS_FILE)
        with self.assertRaises(FileOperationError):
            tm2._load_tickets()
        tm2.teardown()


# ═══════════════════════════════════════════════════════════════
# 8. ITIL Module Tests
# ═══════════════════════════════════════════════════════════════

class TestITILModules(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)
        self.incident_mgr = IncidentManager(self.tm)
        self.sla_mgr      = SLAManager(self.tm)

    def tearDown(self):
        self.tm.teardown()

    def test_incident_logged(self):
        """IncidentManager creates an IncidentTicket."""
        t = self.incident_mgr.log_incident(
            employee_name="Karen",
            department="IT",
            issue_description="Server down",
            category="Server Down",
        )
        self.assertIsInstance(t, IncidentTicket)

    def test_incident_resolved(self):
        """IncidentManager.resolve() sets status to Resolved."""
        t = self.incident_mgr.log_incident(
            employee_name="Leo",
            department="IT",
            issue_description="Internet down",
            category="Network",
        )
        self.incident_mgr.resolve(t.ticket_id, "Router restarted.")
        self.assertEqual(self.tm.get_ticket(t.ticket_id).status, "Resolved")

    def test_change_lifecycle(self):
        """ChangeManager full lifecycle: Request→Approve→Implement→Verify→Close."""
        import itil as _itil
        _itil.CHANGES_FILE = os.path.join(self.tmp, "changes.json")
        cm = ChangeManager()
        cr = cm.request_change("Patch Server", "Apply OS patches", "Admin", "Standard")
        self.assertEqual(cr.status, "Requested")
        cm.approve_change(cr.change_id, "CAB Team")
        self.assertEqual(cm._get_change(cr.change_id).status, "Approved")
        cm.implement_change(cr.change_id)
        self.assertEqual(cm._get_change(cr.change_id).status, "Implementing")
        cm.verify_change(cr.change_id)
        cm.close_change(cr.change_id)
        self.assertEqual(cm._get_change(cr.change_id).status, "Closed")

    def test_sla_report_structure(self):
        """SLAManager.get_sla_report() returns all priority keys."""
        report = self.sla_mgr.get_sla_report()
        for p in ("P1", "P2", "P3", "P4"):
            self.assertIn(p, report)
            self.assertIn("compliance_pct", report[p])


# ═══════════════════════════════════════════════════════════════
# 9. Utility & Advanced Python Tests
# ═══════════════════════════════════════════════════════════════

class TestUtils(unittest.TestCase):

    def test_generate_ticket_id_format(self):
        tid = generate_ticket_id()
        self.assertTrue(tid.startswith("TKT-"))
        self.assertEqual(len(tid), 12)  # "TKT-" + 8 hex chars

    def test_count_by_priority(self):
        tickets = [
            {"priority": "P1"}, {"priority": "P1"}, {"priority": "P2"}, {"priority": "P3"},
        ]
        result = count_by_priority(tickets)
        self.assertEqual(result["P1"], 2)
        self.assertEqual(result["P2"], 1)

    def test_average_resolution_hours(self):
        tickets = [
            {"status": "Resolved", "created_at": "2026-01-01 08:00:00",
             "resolved_at": "2026-01-01 10:00:00"},
        ]
        avg = average_resolution_hours(tickets)
        self.assertAlmostEqual(avg, 2.0, places=1)

    def test_priority_iterator(self):
        it = PriorityIterator()
        priorities = list(it)
        self.assertEqual(priorities, ["P1", "P2", "P3", "P4"])

    def test_page_generator(self):
        items = list(range(25))
        pages = list(ticket_page_generator(items, page_size=10))
        self.assertEqual(len(pages), 3)
        self.assertEqual(len(pages[0]), 10)
        self.assertEqual(len(pages[2]), 5)

    def test_truncate(self):
        self.assertEqual(truncate("hello", 10), "hello")
        self.assertEqual(len(truncate("a" * 100, 50)), 50)

    def test_mask_sensitive(self):
        s = "password=secret123"
        self.assertNotIn("secret123", mask_sensitive(s))

    def test_validate_status_valid(self):
        self.assertEqual(validate_status("open"), "Open")
        self.assertEqual(validate_status("in progress"), "In Progress")


# ═══════════════════════════════════════════════════════════════
# 10. Report Generator Tests
# ═══════════════════════════════════════════════════════════════

class TestReports(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = _make_tm(self.tmp)
        # Redirect reports directory
        import reports as _rep
        self._orig_rdir = _rep.REPORTS_DIR
        _rep.REPORTS_DIR = os.path.join(self.tmp, "reports")
        os.makedirs(_rep.REPORTS_DIR, exist_ok=True)
        self.rg = ReportGenerator(self.tm)

    def tearDown(self):
        import reports as _rep
        _rep.REPORTS_DIR = self._orig_rdir
        self.tm.teardown()

    def _add_tickets(self):
        for i in range(3):
            self.tm.create_ticket(
                employee_name=f"User{i}",
                department="IT",
                issue_description="Laptop slow",
                category="Performance",
                priority="P3",
            )

    def test_daily_report_returns_dict(self):
        self._add_tickets()
        report = self.rg.daily_report()
        self.assertIsInstance(report, dict)
        self.assertIn("total_tickets", report)

    def test_monthly_report_returns_dict(self):
        self._add_tickets()
        report = self.rg.monthly_report()
        self.assertIsInstance(report, dict)
        self.assertIn("most_common_issue", report)

    def test_daily_report_counts_correctly(self):
        self._add_tickets()
        report = self.rg.daily_report()
        self.assertGreaterEqual(report["total_tickets"], 3)


# ═══════════════════════════════════════════════════════════════
# Run all tests
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  AUTOMATED ITIL SERVICE DESK — TEST SUITE")
    print("=" * 70)
    unittest.main(verbosity=2)
