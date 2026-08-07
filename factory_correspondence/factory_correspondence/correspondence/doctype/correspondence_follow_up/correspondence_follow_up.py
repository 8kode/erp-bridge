import frappe
from frappe.model.document import Document


class CorrespondenceFollowUp(Document):
    def before_insert(self):
        if not self.followed_up_by:
            self.followed_up_by = frappe.session.user
