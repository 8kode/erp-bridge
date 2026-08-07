app_name = "factory_correspondence"
app_title = "Factory Correspondence"
app_publisher = "Factory Correspondence"
app_description = "Correspondence Management System for ERPNext v16"
app_email = "admin@example.com"
app_license = "MIT"

# ------------------------------------------------------------------
# Installation
# ------------------------------------------------------------------
after_install = "factory_correspondence.install.after_install"

# ------------------------------------------------------------------
# Document Events (business event action log)
# ------------------------------------------------------------------
doc_events = {
    "Correspondence": {
        "on_update": "factory_correspondence.factory_correspondence.correspondence.doctype.correspondence.correspondence.log_status_change",
    },
    "Correspondence Task": {
        "on_update": "factory_correspondence.factory_correspondence.correspondence.doctype.correspondence_task.correspondence_task.log_task_change",
    },
}

# ------------------------------------------------------------------
# Permissions (confidentiality enforcement)
# ------------------------------------------------------------------
has_permission = {
    "Correspondence": "factory_correspondence.factory_correspondence.correspondence.doctype.correspondence.correspondence.has_permission",
}

permission_query_conditions = {
    "Correspondence": "factory_correspondence.factory_correspondence.correspondence.doctype.correspondence.correspondence.get_permission_query_conditions",
}

# ------------------------------------------------------------------
# Scheduled Tasks
# ------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "factory_correspondence.tasks.mark_overdue_tasks",
        "factory_correspondence.tasks.send_reminders_and_escalations",
    ],
}

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
fixtures = [
    {
        "dt": "Role",
        "filters": [
            [
                "name",
                "in",
                [
                    "Correspondence Clerk",
                    "Correspondence Supervisor",
                    "Correspondence Officer",
                    "Executive Manager",
                    "Auditor",
                ],
            ]
        ],
    },
]
