# Production Board payload

Each `production_board_v*.json` snapshot is generated from a reviewed production
workbook and committed with its migration patch. Do not deploy a patch until its
User Map and Department Map entries have been reviewed.

The workbook must provide:

| Sheet | Required columns |
| --- | --- |
| User Map | `Workbook label`, `ERP user email` |
| Department Map | `Workbook department`, `ERP Department name` |

Generate a payload from the bench root:

```bash
python apps/dieture_board/tools/build_production_board_payload.py \
  /path/to/Dieture_Board.xlsx \
  apps/dieture_board/dieture_board/data/production_board_v1.json
```

If a reviewed workbook has no mapping sheets, reuse a previously reviewed
payload's maps explicitly. A non-date Board target must be supplied as an
explicit reviewed override; the builder rejects other incomplete Board rows.

```bash
python apps/dieture_board/tools/build_production_board_payload.py \
  /path/to/Dieture_Board.xlsx \
  apps/dieture_board/dieture_board/data/production_board_v2.json \
  --version 2 \
  --maps-from apps/dieture_board/dieture_board/data/production_board_v1.json \
  --bet-by-when 4=2026-11-02
```

Review the generated JSON, add the versioned patch module to `patches.txt`,
then deploy with `bench --site erp.dieture.com migrate`.
