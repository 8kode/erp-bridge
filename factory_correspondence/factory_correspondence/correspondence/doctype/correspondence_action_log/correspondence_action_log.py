import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class CorrespondenceActionLog(Document):
    def before_insert(self):
        self.action_by = frappe.session.user
        self.action_datetime = now_datetime()

    def on_trash(self):
        if "System Manager" not in frappe.get_roles():
            frappe.throw(
                _("Action Log entries cannot be deleted."), frappe.PermissionError
            )
