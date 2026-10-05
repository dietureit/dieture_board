import json
from pathlib import Path
from unittest.mock import patch

import frappe
from frappe.tests import UnitTestCase

from dieture_board.production_import import import_production_payload


PAYLOAD_PATH = Path(frappe.get_app_path("dieture_board")) / "data" / "production_board_v2.json"


class TestProductionImport(UnitTestCase):
	def test_disabled_user_stops_before_any_upsert(self):
		payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))

		with (
			patch("dieture_board.production_import._is_local_demo_board", return_value=False),
			patch("dieture_board.production_import.frappe.db.exists", return_value=False),
			patch("dieture_board.production_import._upsert_scorecard") as upsert_scorecard,
		):
			with self.assertRaises(frappe.ValidationError):
				import_production_payload(payload)

		upsert_scorecard.assert_not_called()
