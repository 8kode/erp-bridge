"""Post-install setup: roles, workflows and default settings."""

import frappe

ROLES = [
    "Correspondence Clerk",
    "Correspondence Supervisor",
    "Correspondence Officer",
    "Executive Manager",
    "Auditor",
]


def after_install():
    create_roles()
    create_workflows()
    set_default_settings()
    frappe.db.commit()


def create_roles():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc(
                {"doctype": "Role", "role_name": role, "desk_access": 1}
            ).insert(ignore_permissions=True)


def _make_workflow(name, doctype, states, transitions):
    if frappe.db.exists("Workflow", name):
        return

    # ensure workflow states / actions exist
    for state in {s["state"] for s in states}:
        if not frappe.db.exists("Workflow State", state):
            frappe.get_doc(
                {"doctype": "Workflow State", "workflow_state_name": state}
            ).insert(ignore_permissions=True)
    for action in {t["action"] for t in transitions}:
        if not frappe.db.exists("Workflow Action Master", action):
            frappe.get_doc(
                {"doctype": "Workflow Action Master", "workflow_action_name": action}
            ).insert(ignore_permissions=True)

    wf = frappe.get_doc(
        {
            "doctype": "Workflow",
            "workflow_name": name,
            "document_type": doctype,
            "workflow_state_field": "status",
            "is_active": 0,
            "send_email_alert": 0,
            "states": states,
            "transitions": transitions,
        }
    )
    wf.insert(ignore_permissions=True)


def create_workflows():
    """Incoming and Outgoing correspondence workflows per documentation.

    Both are installed inactive; activate the one matching your process
    (only one active workflow per doctype is allowed by Frappe).
    """
    incoming_states = [
        {"state": "Draft", "doc_status": "0", "allow_edit": "Correspondence Clerk"},
        {"state": "Registered", "doc_status": "0", "allow_edit": "Correspondence Clerk"},
        {"state": "Under Review", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "Assigned", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "In Progress", "doc_status": "0", "allow_edit": "Correspondence Officer"},
        {"state": "Waiting", "doc_status": "0", "allow_edit": "Correspondence Officer"},
        {"state": "Completed", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "Closed", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "Rejected", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "Cancelled", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
    ]
    incoming_transitions = [
        {"state": "Draft", "action": "Register", "next_state": "Registered", "allowed": "Correspondence Clerk"},
        {"state": "Registered", "action": "Review", "next_state": "Under Review", "allowed": "Correspondence Supervisor"},
        {"state": "Under Review", "action": "Assign", "next_state": "Assigned", "allowed": "Correspondence Supervisor"},
        {"state": "Under Review", "action": "Reject", "next_state": "Rejected", "allowed": "Correspondence Supervisor"},
        {"state": "Assigned", "action": "Start", "next_state": "In Progress", "allowed": "Correspondence Officer"},
        {"state": "In Progress", "action": "Wait", "next_state": "Waiting", "allowed": "Correspondence Officer"},
        {"state": "Waiting", "action": "Resume", "next_state": "In Progress", "allowed": "Correspondence Officer"},
        {"state": "In Progress", "action": "Complete", "next_state": "Completed", "allowed": "Correspondence Officer"},
        {"state": "Completed", "action": "Close", "next_state": "Closed", "allowed": "Correspondence Supervisor"},
        {"state": "Registered", "action": "Cancel", "next_state": "Cancelled", "allowed": "Correspondence Supervisor"},
    ]
    _make_workflow(
        "Incoming Correspondence Workflow",
        "Correspondence",
        incoming_states,
        incoming_transitions,
    )

    outgoing_states = [
        {"state": "Draft", "doc_status": "0", "allow_edit": "Correspondence Clerk"},
        {"state": "Under Review", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "Returned for Correction", "doc_status": "0", "allow_edit": "Correspondence Clerk"},
        {"state": "Approved", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "Registered", "doc_status": "0", "allow_edit": "Correspondence Clerk"},
        {"state": "Sent", "doc_status": "0", "allow_edit": "Correspondence Clerk"},
        {"state": "Closed", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
        {"state": "Cancelled", "doc_status": "0", "allow_edit": "Correspondence Supervisor"},
    ]
    outgoing_transitions = [
        {"state": "Draft", "action": "Submit for Review", "next_state": "Under Review", "allowed": "Correspondence Clerk"},
        {"state": "Under Review", "action": "Return for Correction", "next_state": "Returned for Correction", "allowed": "Correspondence Supervisor"},
        {"state": "Returned for Correction", "action": "Submit for Review", "next_state": "Under Review", "allowed": "Correspondence Clerk"},
        {"state": "Under Review", "action": "Approve", "next_state": "Approved", "allowed": "Correspondence Supervisor"},
        {"state": "Approved", "action": "Register", "next_state": "Registered", "allowed": "Correspondence Clerk"},
        {"state": "Registered", "action": "Send", "next_state": "Sent", "allowed": "Correspondence Clerk"},
        {"state": "Sent", "action": "Close", "next_state": "Closed", "allowed": "Correspondence Supervisor"},
        {"state": "Draft", "action": "Cancel", "next_state": "Cancelled", "allowed": "Correspondence Supervisor"},
    ]
    _make_workflow(
        "Outgoing Correspondence Workflow",
        "Correspondence",
        outgoing_states,
        outgoing_transitions,
    )


def set_default_settings():
    settings = frappe.get_single("Correspondence Settings")
    if not settings.sla_normal_days:
        settings.first_reminder_days = 2
        settings.second_reminder_days = 0
        settings.escalation_days = 2
        settings.sla_urgent_days = 2
        settings.sla_high_days = 3
        settings.sla_normal_days = 7
        settings.sla_low_days = 15
        settings.enable_email_notifications = 1
        settings.escalation_role = "Correspondence Supervisor"
        settings.save(ignore_permissions=True)
