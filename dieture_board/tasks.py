import frappe
from frappe.utils import nowdate, formatdate
from dieture_board.utils import users_with_role

def refresh_all_statuses():
    """Daily. Statuses depend on today's date, so recompute without anyone saving."""
    for name in frappe.get_all("Bet", filters={"active": 1}, pluck="name"):
        frappe.get_doc("Bet", name).refresh_status_only()
    for name in frappe.get_all("Promise", filters={"accepted": 0}, pluck="name"):
        frappe.get_doc("Promise", name).refresh_status_only()
    for name in frappe.get_all("Parking Lot Item", filters={"status": ["!=", "Archive"]}, pluck="name"):
        frappe.get_doc("Parking Lot Item", name).refresh_status_only()
    frappe.db.commit()

def thursday_update_reminder():
    owners = frappe.get_all("Bet", filters={"active": 1}, fields=["bet_owner", "short_name", "rank"])
    by_owner = {}
    for o in owners:
        by_owner.setdefault(o.bet_owner, []).append(f"Bet {o.rank} - {o.short_name}")
    for user, bets in by_owner.items():
        frappe.sendmail(recipients=[user], subject="Thursday: update your Board row (5 minutes)",
            message="<p>Please update next step, colour and date for:</p><ul>" + "".join(f"<li>{b}</li>" for b in bets) + "</ul>"
                    "<p>Rows not updated for 7 days turn RED (stale) by themselves.</p>")

def sunday_red_digest():
    refresh_all_statuses()
    reds = frappe.get_all("Bet", filters={"active": 1, "effective_status": ["in", ["RED", "RED (stale)"]]},
                          fields=["rank", "short_name", "bet_owner", "effective_status", "blocker", "who_can_unblock"], order_by="rank asc")
    overdue = frappe.get_all("Promise", filters={"status": ["in", ["Overdue", "Receiver Overdue"]]},
                             fields=["bet_short_name", "deliverable", "maker", "receiver", "status", "days_overdue", "due_date"], order_by="days_overdue desc")
    stale_recv = frappe.get_all("Promise", filters={"status": "Awaiting Acceptance"}, fields=["bet_short_name", "deliverable", "receiver", "acceptance_due"])
    html = ["<h3>Sunday RED digest - " + formatdate(nowdate(), "d MMM yyyy") + "</h3>"]
    html.append("<h4>RED bets</h4>" + ("<ul>" + "".join(
        f"<li><b>Bet {r.rank} - {r.short_name}</b> ({r.effective_status}) owner {r.bet_owner}. Blocker: {r.blocker or '-'}; unblock: {r.who_can_unblock or '-'}</li>" for r in reds) + "</ul>" if reds else "<p>None.</p>"))
    html.append("<h4>Overdue promises</h4>" + ("<ul>" + "".join(
        f"<li>[{o.bet_short_name}] {o.deliverable} - {o.status} by {o.days_overdue} days (maker {o.maker}, receiver {o.receiver})</li>" for o in overdue) + "</ul>" if overdue else "<p>None.</p>"))
    html.append("<h4>Awaiting acceptance (receiver clock running)</h4>" + ("<ul>" + "".join(
        f"<li>[{s.bet_short_name}] {s.deliverable} - receiver {s.receiver}, due {formatdate(s.acceptance_due, 'd MMM')}</li>" for s in stale_recv) + "</ul>" if stale_recv else "<p>None.</p>"))
    html.append("<p>Only RED rows are discussed. Rank settles conflicts. Blocked more than 48h goes to the Chief of Staff, not the CEO.</p>")
    recipients = users_with_role("Chief of Staff")
    if recipients:
        frappe.sendmail(recipients=recipients, subject="Sunday RED digest - Dieture Board", message="".join(html))
