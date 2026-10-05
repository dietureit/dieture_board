import importlib.util
import json
from pathlib import Path
from unittest import TestCase


APP_ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = APP_ROOT / "tools" / "build_production_board_payload.py"
PAYLOAD_PATH = APP_ROOT / "dieture_board" / "data" / "production_board_v2.json"


def _builder_module():
	spec = importlib.util.spec_from_file_location("production_payload_builder", BUILDER_PATH)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


class _Sheet:
	def __init__(self, rows):
		self.rows = rows

	def iter_rows(self, min_row, values_only):
		return iter(self.rows)


def _board_row(rank, **values):
	row = [None] * 30
	row[0] = rank
	for column, value in values.items():
		row[int(column)] = value
	return tuple(row)


class TestProductionPayloadBuilder(TestCase):
	def test_v2_snapshot_includes_reconciled_records(self):
		payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))

		self.assertEqual(
			payload["manifest"],
			{
				"scorecards": 3,
				"bets": 6,
				"promises": 60,
				"standing_numbers": 0,
				"future_bets": 9,
				"parking_lot": 5,
			},
		)
		junior_meals = next(record for record in payload["bets"] if record["rank"] == 4)
		self.assertEqual(junior_meals["short_name"], "Junior Meals")
		self.assertEqual(junior_meals["by_when"], "2026-11-02")
		self.assertEqual(
			len([record for record in payload["promises"] if record["bet_rank"] == 4]),
			3,
		)
		self.assertNotIn(7, {record["rank"] for record in payload["bets"]})
		self.assertTrue(all(record["unlocking_bet_name"] for record in payload["future_bets"]))
		self.assertTrue(all(record["unlocking_status"] for record in payload["future_bets"]))

	def test_placeholder_rank_is_ignored(self):
		builder = _builder_module()
		placeholder = _board_row(7, **{"9": "Margin", "18": "Operations", "22": "G"})

		self.assertEqual(builder._bets(_Sheet([placeholder]), {}), [])

	def test_partial_bet_fails_instead_of_being_dropped(self):
		builder = _builder_module()
		partial = _board_row(
			8,
			**{
				"3": "Partial bet",
				"4": "Move a score",
				"5": "1",
				"6": "2",
				"7": "%",
				"9": "Margin",
				"11": "Prove it",
				"14": "Run a test",
				"17": "Owner",
				"22": "G",
			},
		)

		with self.assertRaisesRegex(ValueError, "Board rank 8 is incomplete: by_when"):
			builder._bets(_Sheet([partial]), {})
