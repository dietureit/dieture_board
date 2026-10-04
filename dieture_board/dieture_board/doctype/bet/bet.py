import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, formatdate, nowdate
from dieture_board.utils import settings, today

TRACKED = ("colour", "next_step", "next_step_by", "next_step_who", "blocker", "number_today", "so_what_today")

class Bet(Document):
    def validate(self):
        self.enforce_wip_and_rank()
        self.touch_last_updated()
        self.compute_status()
        self.one_sentence = self.build_sentence()

    def enforce_wip_and_rank(self):
        if not self.active:
            return
        s = settings()
        others = frappe.get_all("Bet", filters={"active": 1, "name": ["!=", self.name or ""]}, fields=["name", "rank"])
        if len(others) + 1 > (s.wip_limit or 7):
            frappe.throw(_("The Board already has {0} active bets. Park one before adding another.").format(s.wip_limit or 7))
        if any(o.rank == self.rank for o in others):
            frappe.throw(_("Rank {0} is already taken. Ranks must be unique so that rank can settle every conflict.").format(self.rank))

    def touch_last_updated(self):
        before = self.get_doc_before_save()
        if not before or any(before.get(f) != self.get(f) for f in TRACKED):
            self.last_updated = nowdate()

    def compute_status(self):
        s = settings()
        self.days_since_update = date_diff(today(), self.last_updated) if self.last_updated else 0
        if self.days_since_update > (s.stale_days or 7):
            self.effective_status = "RED (stale)"
        else:
            self.effective_status = {"G": "GREEN", "Y": "YELLOW", "R": "RED"}.get(self.colour, "")

    def build_sentence(self):
        nxt = ""
        if self.next_step:
            nxt = " Next: {0}{1}{2}.".format(
                self.next_step,
                " by " + formatdate(self.next_step_by, "d MMM") if self.next_step_by else "",
                " (" + self.next_step_who + ")" if self.next_step_who else "")
        return ("Bet {rank} - {name}. THEN WHAT: {tw}, from {a} to {b} {u} by {d}. "
                "SO WHAT we test first: {sw}. WHAT: {w}. Owner: {o}.{n}").format(
            rank=self.rank, name=self.short_name, tw=self.then_what, a=self.number_today, b=self.number_want,
            u=self.unit, d=formatdate(self.by_when, "d MMM yyyy"), sw=self.so_what, w=self.what,
            o=self.bet_owner, n=nxt)

    def refresh_status_only(self):
        """Used by the daily job: recompute without triggering touch_last_updated."""
        self.compute_status()
        self.db_set({"days_since_update": self.days_since_update, "effective_status": self.effective_status}, update_modified=False)
