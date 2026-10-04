from frappe.model.document import Document
from frappe.utils import date_diff, getdate
from dieture_board.utils import today

class ParkingLotItem(Document):
    def validate(self):
        self.compute_status()

    def compute_status(self):
        t = today()
        self.days_parked = date_diff(t, self.parked_on) if self.parked_on else 0
        if self.days_parked > 90 and not self.still_wanted:
            self.status = "Archive"
        elif self.revisit_by and t > getdate(self.revisit_by):
            self.status = "Revisit Now"
        else:
            self.status = "Frozen"

    def refresh_status_only(self):
        self.compute_status()
        self.db_set({"days_parked": self.days_parked, "status": self.status}, update_modified=False)
