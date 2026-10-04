import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Score", "fieldname": "score", "width": 110},
        {"label": "What it means", "fieldname": "definition", "width": 320},
        {"label": "Baseline", "fieldname": "baseline", "width": 110},
        {"label": "Now", "fieldname": "current", "width": 110},
        {"label": "Target", "fieldname": "target", "width": 110},
        {"label": "Bets pushing it (main)", "fieldname": "main_bets", "fieldtype": "Int", "width": 120},
        {"label": "Bets that also help", "fieldname": "also_bets", "fieldtype": "Int", "width": 120},
        {"label": "System says", "fieldname": "says", "width": 300},
    ]
    data = frappe.get_all("Scorecard Entry", fields=["score", "definition", "baseline", "current", "target"])
    for d in data:
        d["main_bets"] = frappe.db.count("Bet", {"active": 1, "main_score": d["score"]})
        d["also_bets"] = frappe.db.count("Bet", {"active": 1, "also_helps": d["score"]})
        d["says"] = "No bet is pushing this score - strategy gap" if d["main_bets"] == 0 else ("Most bets push this one score - check balance" if d["main_bets"] >= 4 else "OK")
    return columns, data
