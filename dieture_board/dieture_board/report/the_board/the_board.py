import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    status_counts = get_status_counts(data)
    return columns, data, None, get_chart(status_counts), get_report_summary(data, status_counts)


def get_columns():
    return [
        {"label": "Rank", "fieldname": "rank", "fieldtype": "Int", "width": 60},
        {"label": "Bet", "fieldname": "name", "fieldtype": "Link", "options": "Bet", "width": 90},
        {"label": "Short name", "fieldname": "short_name", "width": 150},
        {"label": "Status", "fieldname": "effective_status", "width": 120},
        {"label": "Score", "fieldname": "main_score", "width": 100},
        {"label": "Owner", "fieldname": "bet_owner", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "By when", "fieldname": "by_when", "fieldtype": "Date", "width": 100},
        {"label": "Open promises", "fieldname": "open_promises", "fieldtype": "Int", "width": 90},
        {"label": "Overdue promises", "fieldname": "overdue_promises", "fieldtype": "Int", "width": 100},
        {"label": "In one sentence", "fieldname": "one_sentence", "width": 700},
    ]


def get_data():
    data = frappe.get_all(
        "Bet",
        filters={"active": 1},
        fields=["name", "rank", "short_name", "effective_status", "main_score", "bet_owner", "by_when", "one_sentence"],
        order_by="rank asc",
    )
    for d in data:
        d["open_promises"] = frappe.db.count("Promise", {"bet": d["name"], "accepted": 0})
        d["overdue_promises"] = frappe.db.count(
            "Promise", {"bet": d["name"], "status": ["in", ["Overdue", "Receiver Overdue"]]}
        )
    return data


def get_status_counts(data):
    counts = {"GREEN": 0, "YELLOW": 0, "RED": 0}
    for bet in data:
        status = "RED" if bet.effective_status in {"RED", "RED (stale)"} else bet.effective_status
        if status in counts:
            counts[status] += 1
    return counts


def get_chart(status_counts):
    return {
        "data": {
            "labels": [_("GREEN"), _("YELLOW"), _("RED")],
            "datasets": [{"name": _("Active bets"), "values": list(status_counts.values())}],
        },
        "type": "donut",
        "colors": ["#16a34a", "#f59e0b", "#dc2626"],
    }


def get_report_summary(data, status_counts):
    overdue_promises = sum(bet.overdue_promises for bet in data)
    return [
        {"value": len(data), "indicator": "Blue", "label": _("Active Bets"), "datatype": "Int"},
        {"value": status_counts["GREEN"], "indicator": "Green", "label": _("GREEN"), "datatype": "Int"},
        {"value": status_counts["YELLOW"], "indicator": "Orange", "label": _("YELLOW"), "datatype": "Int"},
        {"value": status_counts["RED"], "indicator": "Red", "label": _("RED"), "datatype": "Int"},
        {"value": overdue_promises, "indicator": "Red", "label": _("Overdue Promises"), "datatype": "Int"},
    ]
