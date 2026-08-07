frappe.ui.form.on("Correspondence", {
  refresh(frm) {
    if (!frm.is_new() && (frm.doc.assignments || []).length) {
      frm.add_custom_button(__("Create Tasks from Assignments"), () => {
        frm.call("create_tasks_from_assignments").then((r) => {
          if (r.message && r.message.length) {
            frappe.msgprint(
              __("Created tasks: {0}", [r.message.join(", ")])
            );
          } else {
            frappe.msgprint(__("All assignments already have tasks."));
          }
        });
      });
    }

    if (!frm.is_new()) {
      frm.add_custom_button(
        __("View Tasks"),
        () => {
          frappe.set_route("List", "Correspondence Task", {
            correspondence: frm.doc.name,
          });
        },
        __("View")
      );
      frm.add_custom_button(
        __("Action Log"),
        () => {
          frappe.set_route("List", "Correspondence Action Log", {
            correspondence: frm.doc.name,
          });
        },
        __("View")
      );
    }
  },

  direction(frm) {
    const series = {
      Incoming: "IN-.YYYY.-.#####.",
      Outgoing: "OUT-.YYYY.-.#####.",
      Internal: "INT-.YYYY.-.#####.",
    };
    if (frm.doc.direction) {
      frm.set_value("naming_series", series[frm.doc.direction]);
    }
  },
});
