"""Idempotent import support for versioned production Board payloads."""

import json
from importlib.resources import files

import frappe
from frappe import _
from frappe.utils import cint


PAYLOAD_FILE = "production_board_v1.json"
SCORES = {"Acquisition", "Retention", "Margin"}
BET_FIELDS = (
	"rank", "active", "door", "short_name", "then_what", "number_today", "number_want", "unit", "by_when",
	"main_score", "also_helps", "so_what", "so_what_today", "so_what_pass_mark", "what", "tiny_test",
	"tiny_test_by", "next_step", "next_step_by", "colour", "blocker", "who_can_unblock", "doors_opened",
	"detail_link",
)
PROMISE_FIELDS = ("deliverable", "due_date", "definition_of_done", "note")
FUTURE_BET_FIELDS = ("title", "unlocking_bet_name", "unlocking_status", "score", "earliest_start", "why_not_inside")
PARKING_LOT_FIELDS = ("idea", "why_existed", "parked_on", "revisit_by")
WORKFLOW_FIELDS = (
	"done", "sent_for_acceptance_on", "accepted", "accepted_on", "rework_returns", "unclear_returns",
	"last_return_reason",
)


def import_embedded_production_data():
	"""Load the deployment payload bundled in ``dieture_board.data``."""
	path = files("dieture_board.data").joinpath(PAYLOAD_FILE)
	with path.open(encoding="utf-8") as payload_file:
		return import_production_payload(json.load(payload_file))


def import_production_payload(payload):
	"""Insert or update an approved production Board payload atomically."""
	if _is_local_demo_board():
		frappe.logger("dieture_board").warning(
			"Skipped production Board payload on di.local because demo Board records are present."
		)
		return {"skipped": "di.local demo Board data is present"}

	_validate_payload(payload)
	users = payload["user_map"]
	departments = payload["department_map"]
	summary = _new_summary()

	for record in payload["scorecards"]:
		_record_result(summary, "scorecards", _upsert_scorecard(record))

	bet_names = {}
	for record in payload["bets"]:
		name, action = _upsert_bet(record, users, departments)
		bet_names[record["rank"]] = name
		_record_result(summary, "bets", action)

	for record in payload["promises"]:
		_record_result(summary, "promises", _upsert_promise(record, bet_names, users, departments))

	for record in payload["standing_numbers"]:
		_record_result(summary, "standing_numbers", _upsert_standing_number(record, users, departments))

	for record in payload["future_bets"]:
		_record_result(summary, "future_bets", _upsert_future_bet(record, bet_names, users))

	for record in payload["parking_lot"]:
		_record_result(summary, "parking_lot", _upsert_parking_lot_item(record, users))

	return summary


def _upsert_scorecard(record):
	name = frappe.db.exists("Scorecard Entry", record["score"])
	doc = frappe.get_doc("Scorecard Entry", name) if name else frappe.new_doc("Scorecard Entry")
	doc.update({key: record.get(key) for key in ("score", "definition", "how_measured", "baseline", "current", "target", "target_date")})
	doc.save(ignore_permissions=True)
	return "updated" if name else "created"


def _upsert_bet(record, users, departments):
	name = frappe.db.exists("Bet", {"rank": record["rank"]})
	doc = frappe.get_doc("Bet", name) if name else frappe.new_doc("Bet")
	doc.update(_fields(record, BET_FIELDS))
	doc.bet_owner = users[record["bet_owner_label"]]
	doc.owner_department = departments.get(record.get("owner_department_label"))
	doc.next_step_who = users.get(record.get("next_step_who_label"))
	doc.save(ignore_permissions=True)

	if record.get("last_updated"):
		doc.db_set("last_updated", record["last_updated"], update_modified=False)
		doc.last_updated = record["last_updated"]
	doc.refresh_status_only()
	return doc.name, "updated" if name else "created"


def _upsert_promise(record, bet_names, users, departments):
	bet = bet_names[record["bet_rank"]]
	name = frappe.db.exists("Promise", {"bet": bet, "deliverable": record["deliverable"]})
	doc = frappe.get_doc("Promise", name) if name else frappe.new_doc("Promise")
	doc.update(_fields(record, PROMISE_FIELDS))
	doc.bet = bet
	doc.bet_short_name = frappe.db.get_value("Bet", bet, "short_name")
	doc.department = departments.get(record.get("department_label"))
	doc.maker = users[record["maker_label"]]
	doc.receiver = users[record["receiver_label"]]

	if not name:
		doc.update(_fields(record.get("workflow", {}), WORKFLOW_FIELDS))
	elif doc.done or doc.accepted:
		doc.due_date = frappe.db.get_value("Promise", name, "due_date")

	doc.save(ignore_permissions=True)
	return "updated" if name else "created"


def _upsert_standing_number(record, users, departments):
	person = users.get(record.get("person_label"))
	filters = {
		"department": departments[record["department_label"]],
		"person": person,
		"role_title": record.get("role_title"),
		"metric": record["metric"],
	}
	name = frappe.db.exists("Standing Number", filters)
	doc = frappe.get_doc("Standing Number", name) if name else frappe.new_doc("Standing Number")
	doc.update(filters)
	doc.update(_fields(record, ("target", "this_week", "as_of", "on_target")))
	doc.on_target = cint(doc.on_target)
	doc.save(ignore_permissions=True)
	return "updated" if name else "created"


def _upsert_future_bet(record, bet_names, users):
	name = frappe.db.exists("Future Bet", {"title": record["title"]})
	doc = frappe.get_doc("Future Bet", name) if name else frappe.new_doc("Future Bet")
	doc.update(_fields(record, FUTURE_BET_FIELDS))
	doc.unlocked_by = bet_names.get(record.get("unlocked_by_rank"))
	doc.future_owner = users[record["future_owner_label"]]
	doc.save(ignore_permissions=True)
	return "updated" if name else "created"


def _upsert_parking_lot_item(record, users):
	name = frappe.db.exists("Parking Lot Item", {"idea": record["idea"]})
	doc = frappe.get_doc("Parking Lot Item", name) if name else frappe.new_doc("Parking Lot Item")
	doc.update(_fields(record, PARKING_LOT_FIELDS))
	doc.item_owner = users[record["item_owner_label"]]
	doc.still_wanted = cint(record.get("still_wanted"))
	doc.save(ignore_permissions=True)
	doc.refresh_status_only()
	return "updated" if name else "created"


def _validate_payload(payload):
	required_sections = ("user_map", "department_map", "scorecards", "bets", "promises", "standing_numbers", "future_bets", "parking_lot")
	missing_sections = [section for section in required_sections if not payload.get(section)]
	if missing_sections:
		frappe.throw(_("Production Board payload is missing: {0}").format(", ".join(missing_sections)))
	actual_counts = {section: len(payload[section]) for section in required_sections[2:]}
	if payload.get("manifest") and payload["manifest"] != actual_counts:
		frappe.throw(_("Production Board payload manifest does not match its records."))

	user_labels = _referenced_user_labels(payload)
	missing_users = sorted(label for label in user_labels if not payload["user_map"].get(label))
	unknown_users = sorted(
		email for email in set(payload["user_map"].values())
		if email and not frappe.db.exists("User", {"name": email, "enabled": 1})
	)
	if missing_users or unknown_users:
		problems = []
		if missing_users:
			problems.append("missing User Map entries: {0}".format(", ".join(missing_users)))
		if unknown_users:
			problems.append("unknown or disabled Users: {0}".format(", ".join(unknown_users)))
		frappe.throw(_("Production Board import stopped — {0}").format("; ".join(problems)))

	department_labels = _referenced_department_labels(payload)
	missing_departments = sorted(label for label in department_labels if not payload["department_map"].get(label))
	unknown_departments = sorted(
		name for name in set(payload["department_map"].values())
		if name and not frappe.db.exists("Department", name)
	)
	if missing_departments or unknown_departments:
		problems = []
		if missing_departments:
			problems.append("missing Department Map entries: {0}".format(", ".join(missing_departments)))
		if unknown_departments:
			problems.append("unknown Departments: {0}".format(", ".join(unknown_departments)))
		frappe.throw(_("Production Board import stopped — {0}").format("; ".join(problems)))

	ranks = [record.get("rank") for record in payload["bets"]]
	if len(ranks) != len(set(ranks)) or not all(ranks):
		frappe.throw(_("Production Board payload must contain unique Bet ranks."))
	if any(record.get("score") not in SCORES for record in payload["scorecards"]):
		frappe.throw(_("Production Board payload has an invalid Scorecard score."))
	if any(record.get("main_score") not in SCORES for record in payload["bets"]):
		frappe.throw(_("Production Board payload has an invalid Bet score."))
	if any(record.get("score") not in SCORES for record in payload["future_bets"]):
		frappe.throw(_("Production Board payload has an invalid Future Bet score."))
	if any(record.get("bet_rank") not in ranks for record in payload["promises"]):
		frappe.throw(_("Production Board payload has a Promise linked to an unknown Bet rank."))
	if any(record.get("unlocked_by_rank") not in ranks for record in payload["future_bets"] if record.get("unlocked_by_rank")):
		frappe.throw(_("Production Board payload has a Future Bet linked to an unknown Bet rank."))


def _referenced_user_labels(payload):
	fields = {
		"bets": ("bet_owner_label", "next_step_who_label"),
		"promises": ("maker_label", "receiver_label"),
		"standing_numbers": ("person_label",),
		"future_bets": ("future_owner_label",),
		"parking_lot": ("item_owner_label",),
	}
	return _referenced_labels(payload, fields)


def _referenced_department_labels(payload):
	return _referenced_labels(payload, {
		"bets": ("owner_department_label",),
		"promises": ("department_label",),
		"standing_numbers": ("department_label",),
	})


def _referenced_labels(payload, fields_by_section):
	labels = set()
	for section, fields in fields_by_section.items():
		for record in payload[section]:
			for field in fields:
				if record.get(field):
					labels.add(record[field])
	return labels


def _is_local_demo_board():
	if frappe.local.site != "di.local":
		return False
	bets = frappe.get_all("Bet", filters={"active": 1}, fields=["rank", "bet_owner"])
	return len(bets) == 7 and all(str(bet.bet_owner).endswith(".invalid") for bet in bets)


def _fields(record, names):
	return {field: record[field] for field in names if field in record}


def _new_summary():
	return {section: {"created": 0, "updated": 0} for section in (
		"scorecards", "bets", "promises", "standing_numbers", "future_bets", "parking_lot",
	)}


def _record_result(summary, section, action):
	summary[section][action] += 1
