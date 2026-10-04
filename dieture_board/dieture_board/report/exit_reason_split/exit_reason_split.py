import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Reason", "fieldname": "reason", "width": 220},
        {"label": "How many", "fieldname": "count", "fieldtype": "Int", "width": 90},
        {"label": "% of cancellations", "fieldname": "pct", "fieldtype": "Percent", "width": 120},
        {"label": "Of which never selected meals", "fieldname": "nonsel", "fieldtype": "Int", "width": 130},
        {"label": "Non-selector share", "fieldname": "nonsel_pct", "fieldtype": "Percent", "width": 110},
        {"label": "System says", "fieldname": "says", "width": 300},
    ]
    s = frappe.get_cached_doc("Board Settings")
    dt = s.cancellation_doctype or "Subscription"
    base = {s.cancelled_filter_field or "status": s.cancelled_filter_value or "Cancelled"}
    if filters.get("from_date"):
        base[s.cancel_date_field or "modified"] = [">=", filters["from_date"]]
    rows = frappe.get_all(dt, filters=base, fields=[s.exit_reason_field or "exit_reason", s.selected_meals_field or "selected_meals"])
    total = len(rows) or 1
    reasons = ["Didn't like meals", "No results / plateaued", "Too expensive", "Service or delivery issue", "Life change / travel", "Other"]
    data = []
    for r in reasons:
        sub = [x for x in rows if (x.get(s.exit_reason_field or "exit_reason") or "Other") == r]
        nonsel = len([x for x in sub if not x.get(s.selected_meals_field or "selected_meals")])
        pct = len(sub) / total * 100
        data.append({"reason": r, "count": len(sub), "pct": pct, "nonsel": nonsel, "nonsel_pct": (nonsel / len(sub) * 100) if sub else 0,
                     "says": "Big enough to fund a bet" if pct >= 25 else ("Too small for an Evidence bet" if pct < 10 else "Medium")})
    data.append({"reason": "Total", "count": len(rows), "pct": 100 if rows else 0, "nonsel": sum(d["nonsel"] for d in data), "nonsel_pct": 0, "says": ""})
    return columns, data
