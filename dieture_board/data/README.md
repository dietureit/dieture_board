# Production Board payload

`production_board_v1.json` is generated from the reviewed production workbook
and committed with the migration patch that imports it. Do not deploy a patch
until its User Map and Department Map entries have been reviewed.

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

Review the generated JSON, add the versioned patch module to `patches.txt`,
then deploy with `bench --site erp.dieture.com migrate`.
