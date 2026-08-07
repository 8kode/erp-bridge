# Factory Correspondence

Correspondence Management System for **ERPNext v16 / Frappe v16**.

Manages the full lifecycle of factory correspondence:

- Incoming / Outgoing / Internal correspondence with naming series `IN-YYYY-#####`, `OUT-YYYY-#####`, `INT-YYYY-#####`
- Classification: type, category, priority (Low/Normal/High/Urgent), confidentiality (Public → Top Secret)
- Department assignments (child table) and executable **Correspondence Tasks** with progress, verification and closure
- Status workflows for incoming and outgoing correspondence (created automatically on install)
- Automatic **Overdue** detection, reminders and escalation via scheduler (configurable in Correspondence Settings)
- Full action log (audit of business events) per correspondence
- Roles: Correspondence Clerk, Correspondence Supervisor, Correspondence Officer, Department Manager, Employee, Executive Manager, Auditor
- Confidentiality enforcement: Secret / Top Secret documents visible only to Supervisor & Executive Manager (and owner)
- Reports: Incoming Register, Outgoing Register, Overdue Tasks, Correspondence Aging, Department Performance
- Dashboard API + Workspace with shortcuts

## Installation

```bash
cd frappe-bench
bench get-app /path/to/factory_correspondence   # or your git url
bench --site yoursite.local install-app factory_correspondence
bench --site yoursite.local migrate
bench restart
```

On install the app automatically creates the roles and the two correspondence workflows.

## Configuration

Open **Correspondence Settings** to configure:

- First / second reminder days
- Escalation days after due date
- SLA response days per priority (Urgent 2, High 3, Normal 7, Low 15 by default)
- Email notifications toggle and escalation role

## Scheduler

Daily jobs (hooks.py):

- `mark_overdue_tasks` – flags tasks past due date as Overdue
- `send_reminders_and_escalations` – reminder & escalation notifications

## License

MIT
