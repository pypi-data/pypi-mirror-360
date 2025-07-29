"""CLI entry point for PPCalendar tool."""

import sys

from .events import (
    interactive_add_event,
    interactive_delete_event,
    get_today_events,
    )
from .ppcalendar import main  # Original calendar rendering logic


COLORS = {
    "heading": "\033[1;34m",    # Bold Blue
    "reset": "\033[0m",         # Reset
    "time": "\033[92m",         # Green
    "birthday": "\033[91m",     # Red
    "рождения": "\033[91m",     # Red
    "python": "\033[94m",       # Blue
    "rust": "\033[91m",         # Red
}


def get_event_color(desc: str) -> str:
    """Return a color code based on keywords in the event description."""
    desc_low = desc.lower()
    for keyword in COLORS:
        if keyword in desc_low and keyword not in ("heading", "reset", "time"):
            return COLORS[keyword]
    return ""


def show_today_events() -> None:
    """Print today's events from the CSV database."""
    events = get_today_events()
    if events:
        print(f"\n📅 {COLORS['heading']}Events for today:{COLORS['reset']}")
        for time, desc in events:
            color = get_event_color(desc)
            print(
                f" - {COLORS['time']}{time or 'All Day'}{COLORS['reset']} "
                f"{color}{desc}{COLORS['reset']}"
            )
    else:
        print(
            f"\n📅 {COLORS['heading']}ppcal add{COLORS['reset']}  "
            f"# to add an event"
        )


def main_cli() -> None:
    """CLI entry logic — handles subcommands."""
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        interactive_add_event()
        return
    elif len(sys.argv) > 1 and sys.argv[1] == "del":
        interactive_delete_event()
        return
    elif len(sys.argv) == 1:
        main()
        show_today_events()
        return
    else:
        main()

