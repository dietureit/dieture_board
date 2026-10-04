frappe.listview_settings["Bet"] = {
  add_fields: ["effective_status", "rank"],
  get_indicator(doc) {
    const m = {"GREEN": "green", "YELLOW": "orange", "RED": "red", "RED (stale)": "red"};
    return [doc.effective_status || "?", m[doc.effective_status] || "gray", "effective_status,=," + doc.effective_status];
  },
  onload(listview) { listview.sort_by = "rank"; listview.sort_order = "asc"; }
};
