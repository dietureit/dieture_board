frappe.ui.form.on("Bet", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("New Promise for this Bet"), () => frappe.new_doc("Promise", {bet: frm.doc.name}));
      frm.add_custom_button(__("Log a Future Bet it unlocks"), () => frappe.new_doc("Future Bet", {unlocked_by: frm.doc.name}));
    }
    frm.set_intro(__("Write it backwards: Problem → THEN WHAT → SO WHAT → WHAT. The colour is yours; the system handles stale."), "blue");
  }
});
