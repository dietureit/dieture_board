import frappe
from frappe.utils import add_days, nowdate

SCORES = [
    ("Acquisition", "How many new customers we win each month, and what each one costs us to win", "New paying subscribers per month; blended cost per new customer (QAR)"),
    ("Retention", "How many new customers are still with us after 60 days (attrition is the opposite)", "Out of 100 new subscribers, how many still subscribed on day 60"),
    ("Margin", "How much money is left from each meal after food, packaging and delivery", "Contribution margin per meal, as % of price"),
]

def after_install():
    for score, definition, how in SCORES:
        if not frappe.db.exists("Scorecard Entry", score):
            frappe.get_doc({"doctype": "Scorecard Entry", "score": score, "definition": definition, "how_measured": how}).insert(ignore_permissions=True)
    s = frappe.get_doc("Board Settings")
    if not s.wip_limit:
        s.update({"wip_limit": 7, "stale_days": 7, "acceptance_workdays": 2, "weekend_days": "4,5"})
        s.save(ignore_permissions=True)
    frappe.db.commit()

def load_sample_data():
    """bench --site <site> execute dieture_board.install.load_sample_data
    Inserts the 7 illustrative bets and a few promises so the team can see the system working. All numbers are pretend."""
    admin = "Administrator"
    bets = [
        dict(rank=1, short_name="Smart defaults", door="Evidence", then_what="Fewer non-selecting customers leave", number_today="41", number_want="28", unit="of 100 leave in 60 days", by_when=add_days(nowdate(), 90), main_score="Retention",
             so_what="Non-selectors receive meals they like WITHOUT having to select - default-day complaints fall", so_what_today="4.2", so_what_pass_mark="1.5 complaints per 1,000 meals",
             what="Preference bubbles at onboarding + a backend rule that assigns defaults from preferences and past ratings", tiny_test="CS hand-picks defaults for 100 non-selectors for 2 weeks; count complaints vs the other non-selectors", colour="G",
             next_step="Pull non-selector cohort and churn split", next_step_by=add_days(nowdate(), 4)),
        dict(rank=2, short_name="New factory live", door="Single path", then_what="MAP production capacity exists", number_today="0", number_want="2,000", unit="meals per day", by_when=add_days(nowdate(), 75), main_score="Margin", also_helps="Retention",
             so_what="Civil Defence approves and one MAP line runs", so_what_today="0", so_what_pass_mark="1 line commissioned, 500 meals/day in week 1", what="New facility with Civil Defence approval and one MAP production line", tiny_test="Not applicable (one road only)", colour="Y",
             next_step="Submit remaining Civil Defence documents", next_step_by=add_days(nowdate(), 6), blocker="Waiting on inspection date", who_can_unblock="Civil Defence"),
        dict(rank=3, short_name="Lego kitchen", door="Evidence", then_what="Kitchen hours per 1,000 meals fall (also: special-diet coverage 55% -> 90%)", number_today="62", number_want="45", unit="kitchen hours per 1,000 meals", by_when=add_days(nowdate(), 165), main_score="Margin", also_helps="Retention",
             so_what="Cooking components and assembling per customer takes fewer hours and serves more diets, same taste", so_what_today="62 h / 55% diets", so_what_pass_mark="<= 55 h AND >= 75% diets on the 5 pilot dishes",
             what="50 dishes broken into components; ERP + app updated AFTER the pilot proves it", tiny_test="5 dishes cooked component-level for 2 weeks on paper sheets; log hours, waste, taste variance, diets servable", colour="G",
             next_step="Pick the 5 pilot dishes and list their components", next_step_by=add_days(nowdate(), 11)),
        dict(rank=4, short_name="New positioning test", door="Evidence", then_what="More strangers who see our ads buy", number_today="2.1", number_want="3.0", unit="of 100 visitors buy", by_when=add_days(nowdate(), 45), main_score="Acquisition",
             so_what="Strangers understand the taste-first message and click through", so_what_today="1.1%", so_what_pass_mark="1.8% click-through on cold audiences", what="Separate landing page + 3 ad sets", tiny_test="4 weeks of cold traffic, existing customers excluded", colour="R",
             next_step="Substantiation page live (launch blocker)", next_step_by=add_days(nowdate(), 8), blocker="Substantiation page not started", who_can_unblock="Marketing lead"),
        dict(rank=5, short_name="Tech ships without CEO", door="Single path", then_what="App releases go out with no founder involvement", number_today="0", number_want="1", unit="releases", by_when=add_days(nowdate(), 75), main_score="Margin",
             so_what="A CTO owns technical decisions, so the CEO is not the bottleneck", so_what_today="0", so_what_pass_mark="CTO in seat", what="Hire a CTO", tiny_test="Not applicable. Milestone: offer accepted", colour="G", next_step="Second call + trial task", next_step_by=add_days(nowdate(), 3)),
        dict(rank=6, short_name="B2B pilot", door="Evidence", then_what="Corporate accounts pay monthly", number_today="0", number_want="120,000", unit="QAR per month (5 accounts)", by_when=add_days(nowdate(), 100), main_score="Acquisition", also_helps="Margin",
             so_what="One company buys, gets delivered daily from the current kitchen, and renews", so_what_today="0", so_what_pass_mark="1 pilot renewed after month 1 at >= 30% margin", what="One pilot account (50 meals/day) from the current kitchen", tiny_test="Sell and serve one pilot for 6 weeks before any capacity is committed", colour="Y",
             next_step="Confirm 200 meals/day B2B capacity with Ops", next_step_by=add_days(nowdate(), 5), blocker="Needs Bet 2 to scale beyond pilot", who_can_unblock="Ops lead"),
        dict(rank=7, short_name="50-dish menu", door="Evidence", then_what="Less prepared food is wasted", number_today="9", number_want="5", unit="% of prepared food wasted", by_when=add_days(nowdate(), 135), main_score="Margin", also_helps="Retention",
             so_what="Most of what customers order is already the same ~50 dishes, so removing the rest loses no orders", so_what_today="unknown", so_what_pass_mark="top 50 dishes >= 95% of orders", what="Fixed menu of 50 dishes instead of 58 rotating", tiny_test="Data pull: share of orders by dish, last 90 days", colour="G",
             next_step="Run dish-volume query", next_step_by=add_days(nowdate(), 4)),
    ]
    names = {}
    for b in bets:
        if frappe.db.exists("Bet", f"BET-{b['rank']}"):
            names[b["rank"]] = f"BET-{b['rank']}"; continue
        doc = frappe.get_doc(dict(doctype="Bet", bet_owner=admin, active=1, **b)).insert(ignore_permissions=True)
        names[b["rank"]] = doc.name
    promises = [
        (1, "Non-selector cohort and churn split, last 6 months", 4, "Sheet with cohort sizes and 60-day churn for selectors vs non-selectors"),
        (1, "Manual preference-based defaults assigned for 100 customers, 2 weeks", 11, "100 customers assigned; complaint log kept daily"),
        (3, "5 pilot dishes broken into component lists", 11, "Component list per dish with weights"),
        (4, "Substantiation page: receipt for every factual claim", 8, "Page live; every claim has a linked source"),
        (6, "Confirm 200 meals/day B2B capacity from current kitchen", 5, "One-line confirmation with the shift plan attached"),
    ]
    for rank, deliverable, days, dod in promises:
        if not frappe.db.exists("Promise", {"bet": names[rank], "deliverable": deliverable}):
            frappe.get_doc(dict(doctype="Promise", bet=names[rank], deliverable=deliverable, maker=admin, receiver=admin,
                                due_date=add_days(nowdate(), days), definition_of_done=dod)).insert(ignore_permissions=True)
    for fb in [("Retail / hotel / airline MAP meals, QAR X per month", 2, "Acquisition", "Needs capacity first; bundling it turns a factory move into a strategy discussion"),
               ("Swipe selection UI for selecting customers", 1, "Retention", "Different cohort from Bet 1; would break attribution"),
               ("Hosted community (SIGNAL bet): +10 retention points for group members", None, "Retention", "Waits for Step 0 baseline and a free Board seat")]:
        if not frappe.db.exists("Future Bet", {"title": fb[0]}):
            frappe.get_doc(dict(doctype="Future Bet", title=fb[0], unlocked_by=names.get(fb[1]) if fb[1] else None, score=fb[2], why_not_inside=fb[3])).insert(ignore_permissions=True)
    frappe.db.commit()
    print("Sample data loaded: 7 bets, 5 promises, 3 future bets. All numbers are pretend.")
