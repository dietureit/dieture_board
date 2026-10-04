import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Rank", "fieldname": "rank", "fieldtype": "Int", "width": 60},
        {"label": "Bet", "fieldname": "name", "fieldtype": "Link", "options": "Bet", "width": 90},
        {"label": "Short name", "fieldname": "short_name", "width": 150},
        {"label": "System says", "fieldname": "effective_status", "width": 100},
        {"label": "Score", "fieldname": "main_score", "width": 100},
        {"label": "Owner", "fieldname": "bet_owner", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "By when", "fieldname": "by_when", "fieldtype": "Date", "width": 100},
        {"label": "Open promises", "fieldname": "open_promises", "fieldtype": "Int", "width": 90},
        {"label": "Overdue promises", "fieldname": "overdue_promises", "fieldtype": "Int", "width": 100},
        {"label": "In one sentence", "fieldname": "one_sentence", "width": 700},
    ]
    data = frappe.get_all("Bet", filters={"active": 1}, fields=["name", "rank", "short_name", "effective_status", "main_score", "bet_owner", "by_when", "one_sentence"], order_by="rank asc")
    for d in data:
        d["open_promises"] = frappe.db.count("Promise", {"bet": d["name"], "accepted": 0})
        d["overdue_promises"] = frappe.db.count("Promise", {"bet": d["name"], "status": ["in", ["Overdue", "Receiver Overdue"]]})
    return columns, data
