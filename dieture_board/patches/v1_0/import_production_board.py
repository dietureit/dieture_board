"""Load the approved production Board payload during migration."""

from dieture_board.production_import import import_embedded_production_data


def execute():
	return import_embedded_production_data()
