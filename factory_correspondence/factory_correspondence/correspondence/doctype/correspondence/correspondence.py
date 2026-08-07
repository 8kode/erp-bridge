import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, now_datetime, nowdate

RESTRICTED_LEVELS = ("Secret", "Top Secret")
PRIVILEGED_ROLES = (
    "Correspondence Supervisor",
    "Executive Manager",
    "System Manager",
    "Administrator",
)

SERIES_BY_DIRECTION = {
    "Incoming": "IN-.YYYY.-.#####.",
    "Outgoing": "OUT-.YYYY.-.#####.",
    "Internal": "INT-.YYYY.-.#####.",
}


class Correspondence(Document):
    def validate(self):
        self.set_naming_series()
        self.validate_dates()
        self.set_registered_date()
        self.set_closed_date()
        self.set_assignment_due_dates()

    def set_naming_series(self):
        expected = SERIES_BY_DIRECTION.get(self.direction)
        if expected and self.naming_series != expected:
            self.naming_series = expected

    def validate_dates(self):
        if (
            self.direction == "Incoming"
            and self.received_date
            and self.correspondence_date
            and self.received_date < self.correspondence_date
        ):
            frappe.throw(_("Received Date cannot be before Correspondence Date"))
        if self.due_date and self.correspondence_date and self.due_date < self.correspondence_date:
            frappe.throw(_("Due Date cannot be before Correspondence Date"))

    def set_registered_date(self):
        if self.status == "Registered" and not self.registered_date:
            self.registered_date = now_datetime()

    def set_closed_date(self):
        if self.status == "Closed" and not self.closed_date:
            self.closed_date = nowdate()
        elif self.status != "Closed":
            self.closed_date = None

    def set_assignment_due_dates(self):
        """Default assignment due dates from SLA settings by priority."""
        settings = frappe.get_cached_doc("Correspondence Settings")
        sla_map = {
            "Urgent": settings.sla_urgent_days or 2,
            "High": settings.sla_high_days or 3,
            "Normal": settings.sla_normal_days or 7,
            "Low": settings.sla_low_days or 15,
        }
        for row in self.assignments or []:
            if not row.due_date:
                days = sla_map.get(row.priority or self.priority or "Normal", 7)
                row.due_date = add_days(nowdate(), int(days))

    def after_insert(self):
        self.db_set("reference_no", self.name, update_modified=False)
        _add_log(self.name, "Created", f"Correspondence created by {frappe.session.user}")

    def on_trash(self):
        frappe.throw(
            _("Correspondence records cannot be deleted. Use Cancel status instead."),
            frappe.PermissionError,
        )

    @frappe.whitelist()
    def create_tasks_from_assignments(self):
        """Create a Correspondence Task for each assignment row without one."""
        created = []
        for row in self.assignments or []:
            exists = frappe.db.exists(
                "Correspondence Task",
                {"correspondence": self.name, "assignment": row.name},
            )
            if exists:
                continue
            task = frappe.get_doc(
                {
                    "doctype": "Correspondence Task",
                    "correspondence": self.name,
                    "assignment": row.name,
                    "task_title": row.instruction or f"Process {self.name}",
                    "description": row.instruction,
                    "department": row.department,
                    "assigned_to": row.assigned_to,
                    "priority": row.priority or self.priority,
                    "start_date": nowdate(),
                    "due_date": row.due_date,
                    "status": "Pending",
                }
            ).insert()
            created.append(task.name)
        if created:
            _add_log(self.name, "Tasks Created", f"Created tasks: {', '.join(created)}")
        return created


# ------------------------------------------------------------------
# Hooks
# ------------------------------------------------------------------

def log_status_change(doc, method=None):
    """doc_events hook - record status changes in the action log."""
    if doc.flags.in_insert:
        return
    old = doc.get_doc_before_save()
    if old and old.status != doc.status:
        _add_log(
            doc.name,
            "Status Change",
            f"Status changed from {old.status} to {doc.status} by {frappe.session.user}",
        )


def _add_log(correspondence, action_type, details):
    try:
        frappe.get_doc(
            {
                "doctype": "Correspondence Action Log",
                "correspondence": correspondence,
                "action_type": action_type,
                "details": details,
            }
        ).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Correspondence action log failed")


# ------------------------------------------------------------------
# Confidentiality enforcement
# ------------------------------------------------------------------

def _is_privileged(user):
    roles = frappe.get_roles(user)
    return any(r in roles for r in PRIVILEGED_ROLES)


def has_permission(doc, ptype="read", user=None):
    user = user or frappe.session.user
    if doc.confidentiality in RESTRICTED_LEVELS:
        if doc.owner == user or _is_privileged(user):
            return True
        return False
    return True


def get_permission_query_conditions(user=None):
    user = user or frappe.session.user
    if _is_privileged(user):
        return ""
    return (
        "(`tabCorrespondence`.`confidentiality` not in ('Secret', 'Top Secret') "
        f"or `tabCorrespondence`.`owner` = {frappe.db.escape(user)})"
    )
