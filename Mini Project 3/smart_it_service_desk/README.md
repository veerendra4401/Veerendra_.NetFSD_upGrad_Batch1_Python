# Smart IT Service Desk — Automated ITIL System

A comprehensive **Python-based ITIL service desk automation system** for managing helpdesk tickets, system monitoring, SLA tracking, and IT service management workflows.

---

## 📁 Project Structure

```
smart_it_service_desk/
├── main.py          # Entry point — interactive CLI menu
├── tickets.py       # OOP ticket classes + TicketManager (CRUD + JSON)
├── monitor.py       # System monitoring (CPU/RAM/Disk/Network)
├── reports.py       # ReportGenerator (Daily & Monthly reports)
├── itil.py          # ITIL workflows: Incident / Problem / Change / SLA
├── utils.py         # Decorators, generators, validators, helpers
├── logger.py        # Centralised rotating-file logger
├── tests.py         # Full unittest test suite (40+ test cases)
├── requirements.txt # Python dependencies
└── data/
    ├── tickets.json     # Ticket persistence store
    ├── problems.json    # Problem records store
    ├── logs.txt         # Rotating log file
    ├── backup.csv       # CSV backup of all tickets
    └── reports/         # Generated daily/monthly report files
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd smart_it_service_desk
pip install -r requirements.txt
```

### 2. Run the interactive CLI
```bash
python main.py
```

### 3. Run all tests
```bash
python -m pytest tests.py -v
# or
python tests.py
```

---

## ✅ Features Implemented

### Ticket Management
| Feature | Status |
|---|---|
| Create Ticket (Incident / Service Request / Problem) | ✔ |
| View All Tickets (sorted, tabular) | ✔ |
| Search Ticket by ID / keyword | ✔ |
| Update Ticket Status | ✔ |
| Close / Resolve Ticket | ✔ |
| Delete Ticket | ✔ |
| Backup to CSV | ✔ |

### Ticket Fields
Each ticket stores: Ticket ID, Employee Name, Department, Issue Description, Category, Priority, Status, Created Date, Resolved Date, Updated Date.

### Priority Rules
| Issue Type | Priority | SLA |
|---|---|---|
| Server Down / Network Down | P1 | 1 Hour |
| Internet Down / Connectivity | P2 | 4 Hours |
| Laptop Slow / High CPU / Disk Full | P3 | 8 Hours |
| Password Reset / Software Install | P4 | 24 Hours |

### ITIL Workflows
- **Incident Management** — Log, categorise, escalate, resolve incidents
- **Problem Management** — Auto-detect recurring issues (≥5 same category) → Problem Record
- **Change Management** — Request → Approve → Implement → Verify → Close
- **SLA Management** — Real-time compliance tracking, breach escalation, warnings

### System Monitoring
Monitors: CPU Usage, Memory Usage, Disk Free %, Network I/O  
Thresholds: CPU > 90%, RAM > 95%, Disk Free < 10%  
On breach: Auto-creates P1 incident ticket + logs CRITICAL alert

### Logging
All events logged to `data/logs.txt` with levels: `INFO`, `WARNING`, `ERROR`, `CRITICAL`  
Uses rotating file handler (5 MB max, 3 backups)

### Reports
- **Daily Report** — Total, Open, Closed, Escalated, High-Priority, SLA Breaches, Priority breakdown
- **Monthly Report** — Most common issue, Avg resolution time, Busiest department, Repeated problems

---

## 🏗️ Python Concepts Demonstrated

| Concept | Where |
|---|---|
| OOP: Inheritance, Polymorphism, Encapsulation | `tickets.py` — Ticket → IncidentTicket / ServiceRequest / ProblemRecord |
| OOP: Constructors, Properties, Static Methods, Special Methods | `tickets.py` |
| Decorators (`@timer`, `@retry`, `@audit_log`) | `utils.py` |
| Generators (`ticket_page_generator`, `alert_generator`) | `utils.py`, `monitor.py` |
| Iterators (`PriorityIterator`) | `utils.py` |
| `map` / `filter` / `reduce` | `utils.py` |
| Custom Exceptions (7 classes) | `utils.py` |
| `try/except/finally` + `raise` | Throughout all modules |
| JSON File Handling (read/write/append) | `tickets.py`, `itil.py` |
| CSV File Handling | `tickets.py`, `reports.py` |
| Context Managers (`with open(...)`) | All file operations |
| Regular Expressions (keyword detection, masking) | `utils.py` |
| `threading` (background monitor) | `monitor.py` |
| `dataclasses` | `monitor.py` — `Alert` |
| List comprehensions, sets, tuples, dicts | Throughout |
| `collections.Counter` | `reports.py`, `itil.py` |
| `functools.reduce` / `functools.wraps` | `utils.py` |

---

## 🧪 Test Coverage

```
TestTicketCreation       (8 tests)  — creation, validation, equality, uniqueness
TestPriorityLogic        (8 tests)  — keyword detection, priority validation
TestSLABreach            (6 tests)  — SLA hours, breach detection, escalation
TestAutoMonitoring       (5 tests)  — alert generation, auto-ticket creation
TestFileOperations       (4 tests)  — JSON save/load, CSV backup, update
TestSearchTickets        (6 tests)  — keyword search, ID lookup, not-found
TestExceptionHandling    (6 tests)  — all custom exceptions, corrupted JSON
TestITILModules          (4 tests)  — incident/change/SLA lifecycle
TestUtils                (8 tests)  — generators, iterators, helpers
TestReports              (3 tests)  — daily/monthly report generation
```

---

## 📊 Data Storage

| File | Format | Purpose |
|---|---|---|
| `data/tickets.json` | JSON | Primary ticket store (loaded on startup) |
| `data/problems.json` | JSON | Problem records |
| `data/changes.json` | JSON | Change records |
| `data/logs.txt` | Plain text | Rotating application log |
| `data/backup.csv` | CSV | Manual/scheduled backup of all tickets |
| `data/reports/*.json` | JSON | Persisted daily/monthly report data |
| `data/reports/*.csv` | CSV | Monthly ticket exports |

---

## 🔧 Debugging

The project is structured for easy IDE debugging:
- All business logic is in clearly named functions/methods
- `@timer` decorator logs execution time of critical operations
- `@audit_log` decorator logs entry/exit for all CRUD operations
- `logger.py` writes `DEBUG`-level traces to `logs.txt`
- Exception stack traces are captured via `log.error(..., exc_info=True)`

To debug in VS Code / PyCharm:
1. Open `main.py`
2. Set breakpoints on any function
3. Run with the debugger — all variables are visible in the watch panel
4. Call stack will show the full ITIL workflow chain

---

## 📋 Requirements

- Python 3.10+
- psutil >= 5.9.0 (system monitoring)

---

## 👤 Author

Automated ITIL Service Desk Project  
Built with Python — Core + OOP + Advanced Concepts + ITIL Workflows
