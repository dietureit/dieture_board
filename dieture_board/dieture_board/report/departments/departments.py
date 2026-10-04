import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 180},
        {"label": "Bets it owns", "fieldname": "bets_owned", "fieldtype": "Int", "width": 100},
        {"label": "Open promises", "fieldname": "open_promises", "fieldtype": "Int", "width": 100},
        {"label": "Overdue promises", "fieldname": "overdue", "fieldtype": "Int", "width": 110},
        {"label": "Standing numbers off target", "fieldname": "off_target", "fieldtype": "Int", "width": 140},
        {"label": "System says", "fieldname": "says", "width": 360},
    ]
    data = []
    for dept in frappe.get_all("Department", filters={"is_group": 0}, pluck="name"):
        bets = frappe.db.count("Bet", {"active": 1, "owner_department": dept})
        openp = frappe.db.count("Promise", {"department": dept, "accepted": 0})
        over = frappe.db.count("Promise", {"department": dept, "status": ["in", ["Overdue", "Receiver Overdue"]]})
        off = frappe.db.count("Standing Number", {"department": dept, "on_target": 0, "this_week": ["!=", ""]})
        says = ("Overdue promise - discuss Sunday" if over else
                "No bet, no promises this quarter - running BAU only" if bets + openp == 0 else "Contributing")
        data.append({"department": dept, "bets_owned": bets, "open_promises": openp, "overdue": over, "off_target": off, "says": says})
    return columns, data
