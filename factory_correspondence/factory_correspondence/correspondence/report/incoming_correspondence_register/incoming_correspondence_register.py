import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    conditions = {"direction": "Incoming"}
    if filters.get("from_date"):
        conditions["correspondence_date"] = [">=", filters["from_date"]]
    if filters.get("department"):
        conditions["department"] = filters["department"]
    if filters.get("status"):
        conditions["status"] = filters["status"]

    columns = [
        {"label": _("Reference"), "fieldname": "name", "fieldtype": "Link", "options": "Correspondence", "width": 160},
        {"label": _("Date"), "fieldname": "correspondence_date", "fieldtype": "Date", "width": 100},
        {"label": _("Received"), "fieldname": "received_date", "fieldtype": "Date", "width": 100},
        {"label": _("Subject"), "fieldname": "subject", "fieldtype": "Data", "width": 260},
        {"label": _("Sender"), "fieldname": "sender_organization", "fieldtype": "Data", "width": 160},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 140},
        {"label": _("Priority"), "fieldname": "priority", "fieldtype": "Data", "width": 90},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
    ]

    data = frappe.get_all(
        "Correspondence",
        filters=conditions,
        fields=[c["fieldname"] for c in columns],
        order_by="correspondence_date desc",
    )
    return columns, data
