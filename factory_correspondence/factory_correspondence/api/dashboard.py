"""Whitelisted dashboard API for correspondence statistics."""

import frappe
from frappe.utils import add_days, nowdate

OPEN_STATUSES = (
    "Registered",
    "Under Review",
    "Assigned",
    "In Progress",
    "Waiting",
    "Waiting External Response",
)


@frappe.whitelist()
def get_dashboard_stats():
    """Return the correspondence dashboard numbers.

    Includes: today's incoming/outgoing, open items, overdue tasks,
    tasks due in 3 days, monthly closed count and unregistered drafts.
    """
    today = nowdate()

    return {
        "incoming_today": frappe.db.count(
            "Correspondence", {"direction": "Incoming", "correspondence_date": today}
        ),
        "outgoing_today": frappe.db.count(
            "Correspondence", {"direction": "Outgoing", "correspondence_date": today}
        ),
        "open_correspondence": frappe.db.count(
            "Correspondence", {"status": ["in", list(OPEN_STATUSES)]}
        ),
        "overdue_tasks": frappe.db.count(
            "Correspondence Task", {"status": "Overdue"}
        ),
        "due_in_3_days": frappe.db.count(
            "Correspondence Task",
            {
                "status": ["in", ["Pending", "In Progress", "Waiting"]],
                "due_date": ["between", [today, add_days(today, 3)]],
            },
        ),
        "closed_this_month": frappe.db.count(
            "Correspondence",
            {
                "status": "Closed",
                "closed_date": [">=", today[:8] + "01"],
            },
        ),
        "drafts": frappe.db.count("Correspondence", {"status": "Draft"}),
    }


@frappe.whitelist()
def get_my_tasks():
    """Open tasks for the logged-in user, oldest due date first."""
    return frappe.get_all(
        "Correspondence Task",
        filters={
            "assigned_to": frappe.session.user,
            "status": ["in", ["Pending", "In Progress", "Waiting", "Overdue"]],
        },
        fields=[
            "name",
            "task_title",
            "correspondence",
            "due_date",
            "status",
            "priority",
            "progress",
        ],
        order_by="due_date asc",
    )
