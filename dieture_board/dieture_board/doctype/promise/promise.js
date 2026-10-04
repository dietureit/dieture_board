frappe.ui.form.on("Promise", {
  refresh(frm) {
    frm.set_intro(__("Agree the definition of done with the receiver BEFORE starting. Receiver has 2 working days to accept or return. A return must quote a line of the definition of done."), "blue");
  }
});
