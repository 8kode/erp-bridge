const doctypes = [
  { name: "Correspondence", desc: "Main record: Incoming / Outgoing / Internal with naming series IN/OUT/INT-YYYY-#####" },
  { name: "Correspondence Assignment", desc: "Child table: department routing with instructions, priority and due dates" },
  { name: "Correspondence Task", desc: "Executable tasks with progress, Overdue detection and verification" },
  { name: "Correspondence Follow Up", desc: "Follow-up records with next follow-up scheduling" },
  { name: "Correspondence Action Log", desc: "Immutable business-event audit trail per correspondence" },
  { name: "Correspondence Settings", desc: "Reminders, escalation and SLA days per priority (2/3/7/15)" },
  { name: "Correspondence Type", desc: "Category master with default response days" },
  { name: "Correspondence Related Document", desc: "Linked documents and attachment metadata" },
]

const features = [
  "Workflows for incoming and outgoing correspondence (auto-created on install)",
  "7 roles: Clerk, Supervisor, Officer, Department Manager, Employee, Executive Manager, Auditor",
  "Secret / Top Secret records hidden from non-privileged users",
  "Daily scheduler: overdue flagging, reminders and escalation emails",
  "5 reports: Incoming & Outgoing Registers, Overdue Tasks, Aging, Department Performance",
  "Dashboard API + Workspace with shortcuts",
  "No delete allowed - cancel-only policy with full audit log",
]

export default function Page() {
  return (
    <main className="min-h-screen bg-background text-foreground font-sans">
      <div className="mx-auto max-w-2xl px-6 py-16">
        <header className="mb-10">
          <p className="text-sm font-mono text-muted-foreground mb-2">ERPNext v16 Custom App</p>
          <h1 className="text-3xl font-bold text-balance mb-3">Factory Correspondence Management</h1>
          <p className="text-muted-foreground leading-relaxed">
            Complete correspondence lifecycle management built from your documentation: registration,
            classification, department assignments, tasks with SLA tracking, escalation, audit logging
            and reports.
          </p>
        </header>

        <a
          href="/factory_correspondence.zip"
          download
          className="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-3 text-primary-foreground font-medium hover:opacity-90 transition-opacity"
        >
          Download factory_correspondence.zip
        </a>

        <section className="mt-12">
          <h2 className="text-lg font-semibold mb-4">DocTypes included</h2>
          <ul className="flex flex-col gap-3">
            {doctypes.map((d) => (
              <li key={d.name} className="rounded-md border border-border p-4">
                <p className="font-mono text-sm font-medium">{d.name}</p>
                <p className="text-sm text-muted-foreground mt-1">{d.desc}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-10">
          <h2 className="text-lg font-semibold mb-4">Features</h2>
          <ul className="flex flex-col gap-2">
            {features.map((f) => (
              <li key={f} className="text-sm text-muted-foreground leading-relaxed">
                {"- "}
                {f}
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-10 rounded-md border border-border p-4">
          <h2 className="text-lg font-semibold mb-3">Installation</h2>
          <pre className="text-xs font-mono bg-muted text-muted-foreground rounded p-3 overflow-x-auto">
            {`# unzip into your bench apps folder
cd frappe-bench
bench get-app /path/to/factory_correspondence
bench --site yoursite install-app factory_correspondence
bench --site yoursite migrate
bench restart`}
          </pre>
          <p className="text-sm text-muted-foreground mt-3 leading-relaxed">
            Roles, workflows and default settings are created automatically on install. Then open
            Correspondence Settings to adjust reminder and SLA days.
          </p>
        </section>
      </div>
    </main>
  )
}
