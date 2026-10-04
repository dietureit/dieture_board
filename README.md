# Dieture Board — Frappe / ERPNext app

The one-place execution system as a Frappe custom app for **ERPNext v15 / Frappe v15**.
Three scores, seven ranked bets (THEN WHAT → SO WHAT → WHAT), promises with definition of done and
receiver acceptance, standing numbers, future bets, parking lot, and the reports that read it all.
The system turns things RED by itself and emails people so nobody has to chase.

> Written to Frappe v15 conventions but **not run against a live site before hand-over**. Expect to spend
> an hour on `bench migrate` warnings and the smoke test below before rolling it out. Treat that hour as the
> developer's first promise: definition of done = the 12 checks in "Smoke test" pass.

## Install

```bash
cd ~/frappe-bench
bench get-app /path/to/dieture_board        # or a git URL once it is in your repo
bench --site <your-site> install-app dieture_board
bench --site <your-site> migrate
bench --site <your-site> execute dieture_board.install.load_sample_data   # optional: 7 pretend bets + promises
bench restart
```

## What gets created

| Thing | Name | Notes |
|---|---|---|
| DocTypes | Bet, Promise, Scorecard Entry, Standing Number, Future Bet, Parking Lot Item, Problem Brief (+ Brief Outcome child), Board Settings (single) | All under module "Dieture Board" |
| Roles | Chief of Staff, Board Owner, Board Viewer, Board Manager | Assign to users. People report is Chief of Staff + Board Manager only |
| Reports | The Board, Scorecard, Departments, People, Exit Reason Split | Script reports, Workspace shortcuts |
| Notifications | Promise Overdue, Receiver Acceptance Overdue, Bet Stale | Email; edit in Setup > Notification |
| Scheduled jobs | Daily status refresh; Thursday 16:00 owner reminder; Sunday 06:00 RED digest to Chief of Staff | `hooks.py` scheduler_events (server timezone) |
| Custom fields | Subscription.exit_reason, Subscription.selected_meals | For the Exit Reason Split. If cancellations live elsewhere, change Board Settings |
| Workspace | Dieture Board | Three cards: Everyone / Chief of Staff and bet owners / Managers only |

## The rules the code enforces

- **Max 7 active bets, unique ranks** (`Bet.validate`). Change the limit in Board Settings.
- **last_updated** is set automatically when colour, next step, next-step date/person, blocker or the two "number today" fields change. Not when someone just opens and saves.
- **RED (stale)** after 7 days without such a change, recomputed daily by the scheduler, not only on save.
- **Promise.status** is computed: On Track / Due This Week (≤3 days) / Overdue / Awaiting Acceptance / Receiver Overdue (past +2 working days, Fri–Sat weekend) / Done.
- **A return re-opens the promise** and requires `last_return_reason`. Increment `rework_returns` (against maker) or `unclear_returns` (against receiver); the status drops back to On Track/Overdue by date.
- **Re-dating a promise** records the old date in `redated_from` automatically.
- **People** report is role-restricted; Bet and Promise are visible to everyone with Board Viewer.

## Smoke test (definition of done for the install)

1. Workspace "Dieture Board" appears; the three cards show.
2. Create an 8th active Bet → blocked with a message. Duplicate rank → blocked.
3. Save a Bet, change only its colour → `last_updated` moves to today; `one_sentence` reads correctly.
4. Set `last_updated` 8 days back via console, run `bench --site <site> execute dieture_board.tasks.refresh_all_statuses` → effective_status = RED (stale).
5. Create a Promise with due date yesterday → status Overdue; "Promise Overdue" notification fires on next scheduler run.
6. Tick Done → status Awaiting Acceptance; `acceptance_due` = +2 working days skipping Fri/Sat.
7. Move `sent_for_acceptance_on` 5 days back, refresh → Receiver Overdue.
8. Tick Accepted → Done; `on_time` = Y/N correctly.
9. Increment `rework_returns` without a reason → blocked; with a reason → promise re-opens.
10. Change a due date → `redated_from` filled.
11. Reports: The Board (sorted by rank), Scorecard (bets per score), Departments, People (hidden from a Board Viewer user).
12. `bench --site <site> execute dieture_board.tasks.sunday_red_digest` → email arrives for users with role Chief of Staff (needs outgoing email configured).

## Mapping to the Excel sample

Excel tab → ERPNext: Board → Bet list + "The Board" report · Promises → Promise · Scorecard → Scorecard Entry + report ·
Departments → Departments report + Standing Number · People → People report · Future Bets → Future Bet ·
Parking Lot → Parking Lot Item · Briefs → Problem Brief · Exit-Reason Split → Exit Reason Split report ·
How It Works / Start Here / Rules → put them in a Wiki page or the Workspace paragraph; they are not data.

## Deliberately not built

Workflow states, approvals, print formats, dashboards with charts, Gantt views. Every one of these is a Parking Lot item
until the Board has run for a quarter. The spec above is the whole thing.
# dieture_board
