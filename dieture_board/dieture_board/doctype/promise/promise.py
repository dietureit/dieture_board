import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, nowdate
from dieture_board.utils import add_workdays, settings, today

class Promise(Document):
    def validate(self):
        if self.done and not self.sent_for_acceptance_on:
            self.sent_for_acceptance_on = nowdate()
        if self.accepted and not self.accepted_on:
            self.accepted_on = nowdate()
        if self.accepted and not self.done:
            self.done = 1
        before = self.get_doc_before_save()
        if before and (self.rework_returns or 0) + (self.unclear_returns or 0) > (before.rework_returns or 0) + (before.unclear_returns or 0):
            if not self.last_return_reason:
                frappe.throw(_("A return needs a reason that points to a line in the definition of done."))
            # a return re-opens the promise
            self.done = 0; self.accepted = 0; self.sent_for_acceptance_on = None; self.accepted_on = None
        if before and before.due_date and getdate(before.due_date) != getdate(self.due_date) and not self.redated_from:
            self.redated_from = before.due_date
        self.compute_status()

    def compute_status(self):
        s = settings(); t = today()
        self.acceptance_due = add_workdays(self.sent_for_acceptance_on, s.acceptance_workdays or 2) if self.sent_for_acceptance_on else None
        if self.accepted:
            self.days_overdue = 0
            delivered = self.sent_for_acceptance_on or self.accepted_on
            self.on_time = "Y" if delivered and getdate(delivered) <= getdate(self.due_date) else "N"
            self.status = "Done"
            return
        self.on_time = ""
        self.days_overdue = max(0, date_diff(t, self.due_date))
        if self.done:
            self.status = "Receiver Overdue" if self.acceptance_due and t > getdate(self.acceptance_due) else "Awaiting Acceptance"
        elif self.days_overdue > 0:
            self.status = "Overdue"
        elif date_diff(self.due_date, t) <= 3:
            self.status = "Due This Week"
        else:
            self.status = "On Track"

    def refresh_status_only(self):
        self.compute_status()
        self.db_set({"status": self.status, "days_overdue": self.days_overdue, "acceptance_due": self.acceptance_due,
                     "on_time": self.on_time}, update_modified=False)
