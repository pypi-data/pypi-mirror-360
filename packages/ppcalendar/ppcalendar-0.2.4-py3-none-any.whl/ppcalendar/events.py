"""Creates csv/(database in the future) and returns events for current day."""

import csv

from datetime import datetime
from pathlib import Path


DAILY = {"*-*-*", "every day", "daily", "каждый день", "ежедневно"}

DB_PATH = Path.home() / ".local" / "share" / "ppcalendar" / "db"
CSV_FILE = DB_PATH / "events.csv"


def ensure_csv_exists() -> None:
    """Ensure the database CSV file exists with headers."""
    if not DB_PATH.exists():
        DB_PATH.mkdir(parents=True)
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "time", "event"])


def parse_date_input(raw: str) -> str:
    """Parse date string into 'YYYY-MM-DD'. Accepts multiple formats."""
    raw = raw.strip()
    if not raw:
        return datetime.today().strftime("%Y-%m-%d")

    raw = raw.replace("/", "-")
    today = datetime.today()

    if raw.lower() in DAILY:
        return "*-*-*"

    parts = raw.split("-")
    try:
        if len(parts) == 3:
            year, month, day = map(int, parts)
        elif len(parts) == 2:
            year = today.year
            month, day = map(int, parts)
        elif len(parts) == 1:
            year = today.year
            month = today.month
            day = int(parts[0])
        else:
            raise ValueError("Invalid date format")

        return datetime(year, month, day).strftime("%Y-%m-%d")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}.\nUse 'daily' or valid dates like YYYY-MM-DD, MM-DD, or DD")
        return ""


def parse_time_input(raw: str) -> str:
    """Convert time input into 'HH:MM'. Return empty string for all-day."""
    if not raw.strip():
        return ""  # All-day event
    raw = raw.strip().replace(":", "")
    if len(raw) == 4:
        hour = int(raw[:2])
        minute = int(raw[2:])
    elif len(raw) == 3:
        hour = int(raw[0])
        minute = int(raw[1:])
    else:
        raise ValueError("Invalid time format.")
    return f"{hour:02}:{minute:02}"


def interactive_add_event() -> None:
    """Prompt user to add a new event interactively."""
    ensure_csv_exists()

    desc = input("📌 Event description (Enter to end): ").strip()
    if not desc:
        print("❗ No description. Cancelled.")
        return

    raw_time = input("⏰ Time (13:00 / 1300) [Enter = all day]: ")
    time = parse_time_input(raw_time)

    date = ""
    while not date:
        raw_date = input("📅 Date (YYYY-MM-DD / MM-DD / DD) [Enter = today]: ")
        date = parse_date_input(raw_date)


    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, time, desc])

    print(f"✅ Event added: {date} {time} - {desc}")

def get_today_events() -> list[tuple[str, str]]:
    """Return list of (time, event) tuples for today."""
    ensure_csv_exists()
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    month_day = now.strftime("-%m-%d")
    day_only = now.strftime("-%d")

    results = []
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_date = row["date"]
            if (
                row_date == today_str
                or (row_date.startswith('*-') and row_date.endswith(month_day))
                or (not row_date.startswith('*-') and row_date.endswith(day_only))
                or row_date == "*-*-*"
            ):
                results.append((row["time"], row["event"]))

    # Sort: All-day (no time) first, then by time
    return sorted(results, key=lambda x: (x[0] != "", x[0]))

def interactive_delete_event() -> None:
    """Prompt user to delete an event from today by selecting it."""
    events = get_today_events()
    if not events:
        print("📭 No events for today.")
        return

    print("\n🗑️ Events for today:")
    for idx, (time, event) in enumerate(events, start=1):
        label = time if time else "All Day"
        print(f"[{idx}] {label} {event}")

    raw_choice = input("\nWhich one to delete [Enter = None]: ").strip()
    if not raw_choice:
        print("❌ Cancelled.")
        return

    try:
        index = int(raw_choice) - 1
        if not (0 <= index < len(events)):
            raise IndexError
    except Exception:
        print("🚫 Invalid selection.")
        return

    to_delete = events[index]
    deleted = False

    rows = []
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (
                not deleted
                and row["time"] == to_delete[0]
                and row["event"] == to_delete[1]
            ):
                deleted = True
                continue  # Skip this row (i.e., delete)
            rows.append(row)

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "time", "event"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"🗑️ Deleted: {to_delete[0]} {to_delete[1]}")

