import frappe
from frappe import _
from frappe.utils import date_diff, nowdate

OPEN_STATUSES = [
    "Registered",
    "Under Review",
    "Assigned",
    "In Progress",
    "Waiting",
    "Waiting External Response",
]


def execute(filters=None):
    filters = filters or {}
    conditions = {"status": ["in", OPEN_STATUSES]}
    if filters.get("direction"):
        conditions["direction"] = filters["direction"]
    if filters.get("department"):
        conditions["department"] = filters["department"]

    columns = [
        {"label": _("Reference"), "fieldname": "name", "fieldtype": "Link", "options": "Correspondence", "width": 160},
        {"label": _("Direction"), "fieldname": "direction", "fieldtype": "Data", "width": 90},
        {"label": _("Subject"), "fieldname": "subject", "fieldtype": "Data", "width": 240},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Date"), "fieldname": "correspondence_date", "fieldtype": "Date", "width": 100},
        {"label": _("Age (days)"), "fieldname": "age_days", "fieldtype": "Int", "width": 90},
        {"label": _("Bucket"), "fieldname": "bucket", "fieldtype": "Data", "width": 100},
    ]

    rows = frappe.get_all(
        "Correspondence",
        filters=conditions,
        fields=["name", "direction", "subject", "department", "status", "correspondence_date"],
        order_by="correspondence_date asc",
    )
    today = nowdate()
    for row in rows:
        age = date_diff(today, row["correspondence_date"]) if row.get("correspondence_date") else 0
        row["age_days"] = age
        if age <= 7:
            row["bucket"] = "0-7"
        elif age <= 14:
            row["bucket"] = "8-14"
        elif age <= 30:
            row["bucket"] = "15-30"
        else:
            row["bucket"] = "30+"

    return columns, rows
