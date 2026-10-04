import frappe
from frappe.utils import getdate, nowdate, add_days, date_diff

def settings():
    return frappe.get_cached_doc("Board Settings")

def weekend():
    s = settings().weekend_days or "4,5"
    return {int(x) for x in s.split(",") if x.strip() != ""}

def add_workdays(d, n):
    d = getdate(d); wk = weekend()
    while n > 0:
        d = add_days(d, 1)
        if d.weekday() not in wk:
            n -= 1
    return d

def today():
    return getdate(nowdate())

def users_with_role(role):
    return [u.parent for u in frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, fields=["parent"])
            if frappe.db.get_value("User", u.parent, "enabled")]
