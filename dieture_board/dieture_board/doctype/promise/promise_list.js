frappe.listview_settings["Promise"] = {
  add_fields: ["status"],
  get_indicator(doc) {
    const m = {"On Track": "green", "Due This Week": "orange", "Overdue": "red", "Awaiting Acceptance": "orange",
               "Receiver Overdue": "red", "Done": "green"};
    return [doc.status, m[doc.status] || "gray", "status,=," + doc.status];
  }
};
