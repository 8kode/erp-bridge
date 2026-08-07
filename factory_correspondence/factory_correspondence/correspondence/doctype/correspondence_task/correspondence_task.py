import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

VERIFY_ROLES = ("Correspondence Supervisor", "Department Manager", "System Manager")


class CorrespondenceTask(Document):
    def validate(self):
        self.validate_dates()
        self.apply_status_side_effects()

    def validate_dates(self):
        if self.start_date and self.due_date and self.due_date < self.start_date:
            frappe.throw(_("Due Date cannot be before Start Date"))

    def apply_status_side_effects(self):
        if self.status == "Completed":
            if not self.completion_date:
                self.completion_date = nowdate()
            if not self.progress or self.progress < 100:
                self.progress = 100
        elif self.status in ("Pending", "In Progress", "Waiting", "Overdue"):
            self.completion_date = None
            self.verified_by = None
            self.verified_date = None

        if self.status == "Verified":
            if not any(r in frappe.get_roles() for r in VERIFY_ROLES):
                frappe.throw(
                    _("Only a Supervisor or Department Manager can verify a task")
                )
            if not self.verified_by:
                self.verified_by = frappe.session.user
                self.verified_date = nowdate()

    def on_trash(self):
        frappe.throw(
            _("Correspondence Tasks cannot be deleted. Use Cancelled status instead."),
            frappe.PermissionError,
        )


def log_task_change(doc, method=None):
    old = doc.get_doc_before_save()
    if not old or old.status == doc.status:
        return
    try:
        frappe.get_doc(
            {
                "doctype": "Correspondence Action Log",
                "correspondence": doc.correspondence,
                "action_type": "Task Status Change",
                "details": (
                    f"Task {doc.name}: {old.status} -> {doc.status} "
                    f"by {frappe.session.user}"
                ),
            }
        ).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Correspondence action log failed")
