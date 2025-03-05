# utils.py
import os
import json
from datetime import datetime, timedelta

REMINDERS_FILE = "reminders.json"

def load_reminders():
    """Load reminders from JSON file."""
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            print("⚠️ Warning: reminders.json is corrupt. Resetting data.")
    return {}

def save_reminders(reminder_data):
    """Persist reminders to the JSON file."""
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminder_data, f, indent=4)

def parse_reminder_time(datetime_str: str):
    """
    Parse a datetime string in the format 'DD-MM-YYYY HH:MM' (24-hour format).
    Returns a tuple (seconds_until_reminder, reminder_datetime) if valid,
    or (None, error_message) if invalid.
    """
    try:
        reminder_dt = datetime.strptime(datetime_str, "%d-%m-%Y %H:%M")
    except ValueError:
        return None, "❌ Invalid time format! Use DD-MM-YYYY HH:MM in 24-hour format."
    
    now = datetime.now()
    if reminder_dt < now:
        return None, "❌ The specified time is in the past. Please specify a future time."
    seconds = (reminder_dt - now).total_seconds()
    return seconds, reminder_dt
