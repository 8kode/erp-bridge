"""Scheduled jobs: overdue detection, reminders and escalation."""

import frappe
from frappe.utils import add_days, date_diff, nowdate

OPEN_TASK_STATUSES = ("Pending", "In Progress", "Waiting")


def mark_overdue_tasks():
    """Flag open tasks whose due date has passed as Overdue.

    Rule: due_date < today AND status not in Completed / Verified / Closed.
    """
    tasks = frappe.get_all(
        "Correspondence Task",
        filters={
            "status": ["in", list(OPEN_TASK_STATUSES)],
            "due_date": ["<", nowdate()],
        },
        pluck="name",
    )
    for name in tasks:
        frappe.db.set_value("Correspondence Task", name, "status", "Overdue")
        _log(
            frappe.db.get_value("Correspondence Task", name, "correspondence"),
            "Task Overdue",
            f"Task {name} became overdue",
        )
    if tasks:
        frappe.db.commit()


def send_reminders_and_escalations():
    settings = frappe.get_single("Correspondence Settings")
    if not settings.enable_email_notifications:
        return

    today = nowdate()
    first_reminder = int(settings.first_reminder_days or 2)
    escalation_days = int(settings.escalation_days or 2)

    tasks = frappe.get_all(
        "Correspondence Task",
        filters={"status": ["in", list(OPEN_TASK_STATUSES) + ["Overdue"]]},
        fields=[
            "name",
            "task_title",
            "assigned_to",
            "due_date",
            "correspondence",
            "department",
            "status",
        ],
    )

    for task in tasks:
        if not task.due_date:
            continue
        days_to_due = date_diff(task.due_date, today)

        # First reminder: N days before due date
        if days_to_due == first_reminder:
            _notify(
                task.assigned_to,
                f"Reminder: Task {task.name} due in {first_reminder} day(s)",
                f"Task <b>{task.task_title}</b> for correspondence {task.correspondence} "
                f"is due on {task.due_date}.",
            )
        # Second reminder: on due date
        elif days_to_due == 0:
            _notify(
                task.assigned_to,
                f"Due today: Task {task.name}",
                f"Task <b>{task.task_title}</b> for correspondence {task.correspondence} "
                f"is due today.",
            )
        # Escalation: N days after due date
        elif days_to_due == -escalation_days:
            recipients = _get_role_users(settings.escalation_role or "Correspondence Supervisor")
            if task.assigned_to:
                recipients.append(task.assigned_to)
            for user in set(recipients):
                _notify(
                    user,
                    f"ESCALATION: Task {task.name} overdue by {escalation_days} day(s)",
                    f"Task <b>{task.task_title}</b> (correspondence {task.correspondence}, "
                    f"department {task.department or '-'}) was due on {task.due_date} "
                    f"and has not been completed.",
                )
            _log(task.correspondence, "Escalation", f"Task {task.name} escalated")


def _get_role_users(role):
    return frappe.get_all(
        "Has Role",
        filters={"role": role, "parenttype": "User"},
        pluck="parent",
    )


def _notify(user, subject, message):
    if not user or user in ("Administrator", "Guest"):
        return
    try:
        # In-app notification
        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "for_user": user,
                "subject": subject,
                "email_content": message,
                "type": "Alert",
            }
        ).insert(ignore_permissions=True)
        # Email
        frappe.sendmail(recipients=[user], subject=subject, message=message)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Correspondence notification failed")


def _log(correspondence, action_type, details):
    if not correspondence:
        return
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
