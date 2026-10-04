app_name = "dieture_board"
app_title = "Dieture Board"
app_publisher = "Dieture"
app_description = "The one-place execution system: Scores, Bets, Promises, Standing Numbers"
app_email = "tech@dieture.com"
app_license = "Proprietary"

after_install = "dieture_board.install.after_install"

fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["Chief of Staff", "Board Owner", "Board Viewer", "Board Manager"]]]},
    {"dt": "Custom Field", "filters": [["module", "=", "Dieture Board"]]},
    {"dt": "Notification", "filters": [["module", "=", "Dieture Board"]]},
]

scheduler_events = {
    "daily": ["dieture_board.tasks.refresh_all_statuses"],
    "cron": {
        # Sunday 06:00 server time: RED digest to the Chief of Staff
        "0 6 * * 0": ["dieture_board.tasks.sunday_red_digest"],
        # Thursday 16:00: reminder to every bet owner to update their row
        "0 16 * * 4": ["dieture_board.tasks.thursday_update_reminder"],
    },
}
