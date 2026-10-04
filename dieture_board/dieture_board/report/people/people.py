import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Person", "fieldname": "user", "fieldtype": "Link", "options": "User", "width": 180},
        {"label": "AS MAKER: promises", "fieldname": "made", "fieldtype": "Int", "width": 90},
        {"label": "Accepted on time", "fieldname": "on_time", "fieldtype": "Int", "width": 90},
        {"label": "Overdue now", "fieldname": "overdue", "fieldtype": "Int", "width": 90},
        {"label": "Awaiting acceptance", "fieldname": "awaiting", "fieldtype": "Int", "width": 90},
        {"label": "Returns for rework", "fieldname": "rework", "fieldtype": "Int", "width": 90},
        {"label": "Say/do", "fieldname": "say_do", "fieldtype": "Percent", "width": 80},
        {"label": "AS RECEIVER: to accept", "fieldname": "to_accept", "fieldtype": "Int", "width": 90},
        {"label": "Acceptances overdue", "fieldname": "recv_overdue", "fieldtype": "Int", "width": 90},
        {"label": "Unclear returns caused", "fieldname": "unclear", "fieldtype": "Int", "width": 90},
        {"label": "Standing numbers off target", "fieldname": "off_target", "fieldtype": "Int", "width": 90},
        {"label": "System says", "fieldname": "says", "width": 360},
    ]
    users = set(frappe.get_all("Promise", pluck="maker")) | set(frappe.get_all("Promise", pluck="receiver")) | set(frappe.get_all("Standing Number", filters={"person": ["!=", ""]}, pluck="person"))
    data = []
    for u in sorted(x for x in users if x):
        made = frappe.db.count("Promise", {"maker": u})
        on_time = frappe.db.count("Promise", {"maker": u, "accepted": 1, "on_time": "Y"})
        overdue = frappe.db.count("Promise", {"maker": u, "status": "Overdue"})
        awaiting = frappe.db.count("Promise", {"maker": u, "status": ["in", ["Awaiting Acceptance", "Receiver Overdue"]]})
        rework = frappe.db.sql("select coalesce(sum(rework_returns),0) from `tabPromise` where maker=%s", u)[0][0]
        to_accept = frappe.db.count("Promise", {"receiver": u, "accepted": 0})
        recv_overdue = frappe.db.count("Promise", {"receiver": u, "status": "Receiver Overdue"})
        unclear = frappe.db.sql("select coalesce(sum(unclear_returns),0) from `tabPromise` where receiver=%s", u)[0][0]
        off = frappe.db.count("Standing Number", {"person": u, "on_target": 0, "this_week": ["!=", ""]})
        say_do = (on_time / made * 100) if made else 0
        if recv_overdue: says = "Holding another person's work: accept or return today"
        elif overdue: says = "Overdue promise - manager to discuss"
        elif made and rework >= 2: says = "Work returned repeatedly - quality conversation"
        elif unclear >= 2: says = "Returning work without a clear definition of done - receiver conversation"
        elif made == 0: says = "No bet this quarter - judged on standing numbers only"
        else: says = "OK"
        data.append(dict(user=u, made=made, on_time=on_time, overdue=overdue, awaiting=awaiting, rework=rework, say_do=say_do,
                         to_accept=to_accept, recv_overdue=recv_overdue, unclear=unclear, off_target=off, says=says))
    return columns, data
