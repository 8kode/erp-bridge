import frappe
from frappe import _
from frappe.utils import date_diff, nowdate


def execute(filters=None):
    filters = filters or {}
    conditions = {
        "status": ["in", ["Pending", "In Progress", "Waiting", "Overdue"]],
        "due_date": ["<", nowdate()],
    }
    if filters.get("department"):
        conditions["department"] = filters["department"]
    if filters.get("assigned_to"):
        conditions["assigned_to"] = filters["assigned_to"]

    columns = [
        {"label": _("Task"), "fieldname": "name", "fieldtype": "Link", "options": "Correspondence Task", "width": 150},
        {"label": _("Title"), "fieldname": "task_title", "fieldtype": "Data", "width": 240},
        {"label": _("Correspondence"), "fieldname": "correspondence", "fieldtype": "Link", "options": "Correspondence", "width": 150},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 140},
        {"label": _("Assigned To"), "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 160},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": _("Days Overdue"), "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Progress"), "fieldname": "progress", "fieldtype": "Percent", "width": 90},
    ]

    rows = frappe.get_all(
        "Correspondence Task",
        filters=conditions,
        fields=["name", "task_title", "correspondence", "department", "assigned_to", "due_date", "status", "progress"],
        order_by="due_date asc",
    )
    today = nowdate()
    for row in rows:
        row["days_overdue"] = date_diff(today, row["due_date"]) if row.get("due_date") else 0

    return columns, rows
