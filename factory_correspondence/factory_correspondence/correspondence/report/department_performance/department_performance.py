import frappe
from frappe import _


def execute(filters=None):
    columns = [
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 200},
        {"label": _("Total Tasks"), "fieldname": "total_tasks", "fieldtype": "Int", "width": 110},
        {"label": _("Completed"), "fieldname": "completed", "fieldtype": "Int", "width": 100},
        {"label": _("Open"), "fieldname": "open", "fieldtype": "Int", "width": 90},
        {"label": _("Overdue"), "fieldname": "overdue", "fieldtype": "Int", "width": 90},
        {"label": _("Completion %"), "fieldname": "completion_pct", "fieldtype": "Percent", "width": 110},
    ]

    data = frappe.db.sql(
        """
        SELECT
            IFNULL(department, 'Unassigned') AS department,
            COUNT(*) AS total_tasks,
            SUM(CASE WHEN status IN ('Completed', 'Verified', 'Closed') THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN status IN ('Pending', 'In Progress', 'Waiting') THEN 1 ELSE 0 END) AS `open`,
            SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END) AS overdue
        FROM `tabCorrespondence Task`
        GROUP BY IFNULL(department, 'Unassigned')
        ORDER BY total_tasks DESC
        """,
        as_dict=True,
    )
    for row in data:
        row["completion_pct"] = (
            (row["completed"] or 0) * 100.0 / row["total_tasks"] if row["total_tasks"] else 0
        )

    return columns, data
