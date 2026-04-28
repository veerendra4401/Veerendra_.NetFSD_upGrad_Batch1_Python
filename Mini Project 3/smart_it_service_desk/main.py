"""
main.py - Entry Point & Interactive CLI Menu
Automated ITIL Service Desk System

Wires all modules together and provides a full interactive command-line interface.
"""

import os
import sys
import traceback
from datetime import datetime

# ── Make sure the package directory is on the path ────────────
sys.path.insert(0, os.path.dirname(__file__))

from logger import get_logger
from tickets import IncidentTicket, ProblemRecord, ServiceRequest, TicketManager
from monitor import Monitor
from itil import ChangeManager, IncidentManager, ProblemManager, SLAManager
from reports import ReportGenerator
from utils import (
    EmptyFieldError,
    InvalidPriorityError,
    InvalidStatusError,
    SLABreachError,
    TicketNotFoundError,
    center_banner,
    VALID_STATUSES,
)

log = get_logger("main")

# ─────────────────────────────────────────────
# Bootstrap
# ─────────────────────────────────────────────

def _bootstrap() -> dict:
    """Initialise all service components and return a context dict."""
    print(center_banner("  AUTOMATED ITIL SERVICE DESK  "))
    print("  Initialising system …")

    tm      = TicketManager()
    monitor = Monitor(ticket_manager=tm, poll_interval=120)
    im      = IncidentManager(tm)
    pm      = ProblemManager(tm)
    cm      = ChangeManager()
    sla     = SLAManager(tm)
    rg      = ReportGenerator(tm)

    log.info("System bootstrapped successfully.")
    print("  System ready.\n")

    return {
        "tm": tm, "monitor": monitor,
        "im": im, "pm": pm, "cm": cm,
        "sla": sla, "rg": rg,
    }


# ─────────────────────────────────────────────
# Input helpers
# ─────────────────────────────────────────────

def _input(prompt: str, required: bool = True) -> str:
    """Prompt user for input; raise EmptyFieldError if required and blank."""
    val = input(f"  {prompt}: ").strip()
    if required and not val:
        raise EmptyFieldError(f"'{prompt}' is required.")
    return val


def _pause() -> None:
    input("\n  Press Enter to continue …")


# ─────────────────────────────────────────────
# Ticket sub-menu handlers
# ─────────────────────────────────────────────

def _create_ticket(ctx: dict) -> None:
    """Interactively create a new ticket."""
    tm: TicketManager = ctx["tm"]
    print("\n" + center_banner(" CREATE NEW TICKET ", char="-"))
    print("  Types: 1=Incident  2=Service Request  3=Problem Record")
    t_choice = _input("Type (1/2/3)", required=False) or "1"
    type_map  = {"1": "IncidentTicket", "2": "ServiceRequest", "3": "ProblemRecord"}
    ticket_type = type_map.get(t_choice, "IncidentTicket")

    employee = _input("Employee Name")
    dept     = _input("Department")
    desc     = _input("Issue Description")
    category = _input("Category")
    priority_raw = _input("Priority (P1/P2/P3/P4 or leave blank for auto)", required=False)
    priority = priority_raw.upper() if priority_raw else None

    # Subclass-specific extras
    extra: dict = {}
    if ticket_type == "IncidentTicket":
        extra["impact"]     = _input("Impact (Low/Medium/High)", required=False) or "Medium"
        extra["urgency"]    = _input("Urgency (Low/Medium/High)", required=False) or "Medium"
        extra["workaround"] = _input("Workaround (leave blank if none)", required=False)
    elif ticket_type == "ServiceRequest":
        extra["requested_service"] = _input("Requested Service")
        extra["approved_by"]       = _input("Approved By", required=False) or "Pending"
    elif ticket_type == "ProblemRecord":
        extra["root_cause"] = _input("Root Cause", required=False) or "Under Investigation"

    ticket = tm.create_ticket(
        employee_name     = employee,
        department        = dept,
        issue_description = desc,
        category          = category,
        ticket_type       = ticket_type,
        priority          = priority,
        **extra,
    )
    print(f"\n  ✔ Ticket created: {ticket.ticket_id}  |  Priority: {ticket.priority}")
    tm.display_ticket(ticket)


def _view_all_tickets(ctx: dict) -> None:
    """Display all tickets in a tabular list."""
    tm: TicketManager = ctx["tm"]
    tickets = tm.get_all_tickets()
    if not tickets:
        print("  No tickets found.")
        return
    print("\n" + center_banner(f" ALL TICKETS ({len(tickets)}) ", char="-"))
    print(f"  {'ID':<14} {'Type':<18} {'Prio':<5} {'Status':<12} {'Employee':<18} {'SLA'}")
    print("  " + "-" * 80)
    for t in tickets:
        sla_flag = "BREACH" if t.is_sla_breached() else f"{t.sla_remaining_hours():+.1f}h"
        print(
            f"  {t.ticket_id:<14} {t.ticket_type_label():<18} {t.priority:<5} "
            f"{t.status:<12} {t.employee_name:<18} {sla_flag}"
        )


def _search_ticket(ctx: dict) -> None:
    """Search tickets by keyword."""
    tm: TicketManager = ctx["tm"]
    keyword = _input("Search keyword")
    results = tm.search_tickets(keyword)
    print(f"\n  Found {len(results)} result(s) for '{keyword}':")
    for t in results:
        print(f"    {t}")


def _view_ticket_detail(ctx: dict) -> None:
    """Display full details of a single ticket."""
    tm: TicketManager = ctx["tm"]
    ticket_id = _input("Ticket ID").upper()
    t = tm.get_ticket(ticket_id)
    tm.display_ticket(t)


def _update_ticket(ctx: dict) -> None:
    """Update the status of an existing ticket."""
    tm: TicketManager = ctx["tm"]
    ticket_id = _input("Ticket ID to update").upper()
    print(f"  Valid statuses: {', '.join(VALID_STATUSES)}")
    new_status = _input("New Status")
    ticket = tm.update_status(ticket_id, new_status)
    print(f"  ✔ Ticket {ticket_id} updated → {ticket.status}")


def _close_ticket(ctx: dict) -> None:
    """Close/Resolve a ticket."""
    tm: TicketManager = ctx["tm"]
    ticket_id = _input("Ticket ID to close").upper()
    tm.update_status(ticket_id, "Closed")
    print(f"  ✔ Ticket {ticket_id} closed.")


def _delete_ticket(ctx: dict) -> None:
    """Delete a ticket (irreversible)."""
    tm: TicketManager = ctx["tm"]
    ticket_id = _input("Ticket ID to DELETE").upper()
    confirm   = _input(f"Confirm delete '{ticket_id}'? (yes/no)")
    if confirm.lower() == "yes":
        msg = tm.delete_ticket(ticket_id)
        print(f"  ✔ {msg}")
    else:
        print("  Deletion cancelled.")


def _ticket_menu(ctx: dict) -> None:
    while True:
        print("\n" + center_banner(" TICKET MANAGEMENT ", char="-"))
        print("  1. Create Ticket")
        print("  2. View All Tickets")
        print("  3. Search Ticket")
        print("  4. View Ticket Detail")
        print("  5. Update Ticket Status")
        print("  6. Close Ticket")
        print("  7. Delete Ticket")
        print("  8. Backup Tickets to CSV")
        print("  0. Back")
        choice = _input("Choice", required=False) or "0"
        try:
            if choice == "1":   _create_ticket(ctx)
            elif choice == "2": _view_all_tickets(ctx)
            elif choice == "3": _search_ticket(ctx)
            elif choice == "4": _view_ticket_detail(ctx)
            elif choice == "5": _update_ticket(ctx)
            elif choice == "6": _close_ticket(ctx)
            elif choice == "7": _delete_ticket(ctx)
            elif choice == "8":
                ctx["tm"].backup_to_csv()
                print("  ✔ Backup complete.")
            elif choice == "0": break
            else: print("  Invalid choice.")
        except (EmptyFieldError, InvalidPriorityError, InvalidStatusError,
                TicketNotFoundError) as exc:
            print(f"\n  ✖ Error: {exc}")
        except Exception as exc:
            log.error("Unexpected error in ticket menu: %s", exc, exc_info=True)
            print(f"\n  ✖ Unexpected error: {exc}")
        _pause()


# ─────────────────────────────────────────────
# Monitoring sub-menu
# ─────────────────────────────────────────────

def _monitor_menu(ctx: dict) -> None:
    monitor: Monitor = ctx["monitor"]
    while True:
        print("\n" + center_banner(" SYSTEM MONITORING ", char="-"))
        print("  1. Take Snapshot Now")
        print("  2. Check Thresholds & Alerts")
        print("  3. View Alert History")
        print("  4. Start Background Monitor")
        print("  5. Stop Background Monitor")
        print("  0. Back")
        choice = _input("Choice", required=False) or "0"
        try:
            if choice == "1":
                snap = monitor.sample()
                monitor.display_snapshot(snap)
            elif choice == "2":
                snap   = monitor.sample()
                alerts = monitor.check_thresholds(snap)
                monitor.display_snapshot(snap)
                if alerts:
                    print(f"  ⚠  {len(alerts)} alert(s) detected!")
                    for a in alerts:
                        print(f"    {a}")
                else:
                    print("  ✔ All metrics within threshold.")
            elif choice == "3":
                hist = monitor.alerts_history
                print(f"\n  Alert History ({len(hist)} entries):")
                for a in hist[-20:]:   # last 20
                    print(f"    {a}")
            elif choice == "4":
                monitor.start_background()
                print("  ✔ Background monitoring started.")
            elif choice == "5":
                monitor.stop()
                print("  ✔ Background monitoring stopped.")
            elif choice == "0":
                break
            else:
                print("  Invalid choice.")
        except Exception as exc:
            log.error("Monitor menu error: %s", exc, exc_info=True)
            print(f"  ✖ Error: {exc}")
        _pause()


# ─────────────────────────────────────────────
# ITIL sub-menu
# ─────────────────────────────────────────────

def _itil_menu(ctx: dict) -> None:
    im: IncidentManager = ctx["im"]
    pm: ProblemManager  = ctx["pm"]
    cm: ChangeManager   = ctx["cm"]
    sla: SLAManager     = ctx["sla"]

    while True:
        print("\n" + center_banner(" ITIL MANAGEMENT ", char="-"))
        print("  1. Log Incident (Incident Mgmt)")
        print("  2. Resolve Incident")
        print("  3. View Open Incidents")
        print("  4. Analyse Recurring Issues (Problem Mgmt)")
        print("  5. View Problem Records")
        print("  6. Request Change (Change Mgmt)")
        print("  7. Approve / Implement / Close Change")
        print("  8. SLA Compliance Report")
        print("  9. Escalate Breached SLA Tickets")
        print(" 10. SLA Warnings (tickets nearing breach)")
        print("  0. Back")
        choice = _input("Choice", required=False) or "0"
        try:
            if choice == "1":
                employee = _input("Employee Name")
                dept     = _input("Department")
                desc     = _input("Issue Description")
                cat      = _input("Category")
                t = im.log_incident(employee, dept, desc, cat)
                print(f"  ✔ Incident logged: {t.ticket_id}  Priority: {t.priority}")

            elif choice == "2":
                tid  = _input("Ticket ID").upper()
                note = _input("Resolution Note", required=False)
                im.resolve(tid, note)
                print(f"  ✔ Incident {tid} resolved.")

            elif choice == "3":
                open_inc = im.get_open_incidents()
                print(f"\n  Open Incidents ({len(open_inc)}):")
                for t in open_inc:
                    print(f"    {t}")

            elif choice == "4":
                new_prs = pm.analyse_recurring_issues()
                if new_prs:
                    print(f"  ⚠  {len(new_prs)} new Problem Record(s) created:")
                    for pr in new_prs:
                        print(f"    {pr.ticket_id} — {pr.category}")
                else:
                    print("  ✔ No new recurring patterns detected (threshold: 5 incidents).")

            elif choice == "5":
                prs = pm.get_all_problems()
                print(f"\n  Problem Records ({len(prs)}):")
                for pr in prs:
                    print(f"    {pr.ticket_id}  |  {pr.category}  |  RC: {pr.root_cause}")

            elif choice == "6":
                title  = _input("Change Title")
                desc   = _input("Description")
                req_by = _input("Requested By")
                ctype  = _input("Type (Standard/Normal/Emergency)", required=False) or "Standard"
                cr = cm.request_change(title, desc, req_by, ctype)
                print(f"  ✔ Change requested: {cr.change_id}")

            elif choice == "7":
                changes = cm.get_all_changes()
                if not changes:
                    print("  No change records found.")
                else:
                    for c in changes:
                        print(f"    {c}")
                    cid = _input("Change ID").upper()
                    print("  Actions: A=Approve  I=Implement  V=Verify  C=Close")
                    action = _input("Action").upper()
                    if action == "A":
                        appr = _input("Approved By")
                        cm.approve_change(cid, appr)
                        print(f"  ✔ Change {cid} approved.")
                    elif action == "I":
                        cm.implement_change(cid)
                        print(f"  ✔ Change {cid} implementation started.")
                    elif action == "V":
                        cm.verify_change(cid)
                        print(f"  ✔ Change {cid} verified.")
                    elif action == "C":
                        cm.close_change(cid)
                        print(f"  ✔ Change {cid} closed.")
                    else:
                        print("  Unknown action.")

            elif choice == "8":
                sla.display_sla_report()

            elif choice == "9":
                escalated = sla.escalate_breached()
                print(f"  ✔ {len(escalated)} ticket(s) escalated.")

            elif choice == "10":
                warnings = sla.generate_warnings()
                if warnings:
                    for w in warnings:
                        print(f"  ⚠  {w}")
                else:
                    print("  ✔ No tickets nearing SLA breach.")

            elif choice == "0":
                break
            else:
                print("  Invalid choice.")

        except (EmptyFieldError, TicketNotFoundError, ValueError) as exc:
            print(f"\n  ✖ Error: {exc}")
        except Exception as exc:
            log.error("ITIL menu error: %s", exc, exc_info=True)
            print(f"\n  ✖ Unexpected error: {exc}")
        _pause()


# ─────────────────────────────────────────────
# Reports sub-menu
# ─────────────────────────────────────────────

def _reports_menu(ctx: dict) -> None:
    rg: ReportGenerator = ctx["rg"]
    while True:
        print("\n" + center_banner(" REPORTS ", char="-"))
        print("  1. Quick Summary")
        print("  2. Daily Report (Today)")
        print("  3. Daily Report (Custom Date)")
        print("  4. Monthly Report (This Month)")
        print("  5. Monthly Report (Custom Month)")
        print("  0. Back")
        choice = _input("Choice", required=False) or "0"
        try:
            if choice == "1":
                rg.quick_summary()
            elif choice == "2":
                rg.daily_report()
            elif choice == "3":
                date_str = _input("Date (YYYY-MM-DD)")
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                rg.daily_report(dt)
            elif choice == "4":
                rg.monthly_report()
            elif choice == "5":
                year  = int(_input("Year (e.g. 2026)"))
                month = int(_input("Month (1-12)"))
                rg.monthly_report(year, month)
            elif choice == "0":
                break
            else:
                print("  Invalid choice.")
        except ValueError as exc:
            print(f"  ✖ Invalid input: {exc}")
        except Exception as exc:
            log.error("Reports menu error: %s", exc, exc_info=True)
            print(f"  ✖ Error: {exc}")
        _pause()


# ─────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────

def main() -> None:
    try:
        ctx = _bootstrap()
    except Exception as exc:
        print(f"FATAL: Could not initialise system — {exc}")
        traceback.print_exc()
        sys.exit(1)

    while True:
        print("\n" + center_banner("  SMART IT SERVICE DESK — MAIN MENU  "))
        ctx["rg"].quick_summary()
        print()
        print("  1. Ticket Management")
        print("  2. System Monitoring")
        print("  3. ITIL Management")
        print("  4. Reports")
        print("  0. Exit")
        choice = _input("Choice", required=False) or "0"
        try:
            if choice == "1":
                _ticket_menu(ctx)
            elif choice == "2":
                _monitor_menu(ctx)
            elif choice == "3":
                _itil_menu(ctx)
            elif choice == "4":
                _reports_menu(ctx)
            elif choice == "0":
                print("\n  Goodbye! Shutting down …")
                ctx["monitor"].stop()
                log.info("System shutdown cleanly.")
                break
            else:
                print("  Invalid choice. Please enter 0-4.")
        except KeyboardInterrupt:
            print("\n  Interrupted. Returning to main menu.")


if __name__ == "__main__":
    main()
