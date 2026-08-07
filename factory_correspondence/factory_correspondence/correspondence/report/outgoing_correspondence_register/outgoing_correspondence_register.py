import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    conditions = {"direction": "Outgoing"}
    if filters.get("from_date"):
        conditions["correspondence_date"] = [">=", filters["from_date"]]
    if filters.get("department"):
        conditions["department"] = filters["department"]
    if filters.get("status"):
        conditions["status"] = filters["status"]

    columns = [
        {"label": _("Reference"), "fieldname": "name", "fieldtype": "Link", "options": "Correspondence", "width": 160},
        {"label": _("Date"), "fieldname": "correspondence_date", "fieldtype": "Date", "width": 100},
        {"label": _("Subject"), "fieldname": "subject", "fieldtype": "Data", "width": 260},
        {"label": _("Recipient"), "fieldname": "recipient_organization", "fieldtype": "Data", "width": 160},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 140},
        {"label": _("Priority"), "fieldname": "priority", "fieldtype": "Data", "width": 90},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": _("Related"), "fieldname": "related_correspondence", "fieldtype": "Link", "options": "Correspondence", "width": 150},
    ]

    data = frappe.get_all(
        "Correspondence",
        filters=conditions,
        fields=[c["fieldname"] for c in columns],
        order_by="correspondence_date desc",
    )
    return columns, data
