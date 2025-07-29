import calendar
import locale
import sys

from datetime import date
from typing import Generator, Iterable, Optional, Union

class CalendarConfig:
    """Configuration constants and color codes."""
    MONTH_WIDTH = 20
    WEEKS_TO_SHOW = 6
    WEEKDAYS_TO_SHOW = 7

    COLORS = {
        'reset': '\033[0m',
        'spring': '\033[30;42m',  # Black on green (Mar-May)
        'summer': '\033[97;41m',  # White on red (Jun-Aug)
        'autumn': '\033[30;43m',  # Black on yellow (Sep-Nov)
        'winter': '\033[30;44m',  # Black on blue (Dec-Feb)
        'weekday': '\033[34m',    # Blue
        'sunday': '\033[91m',     # Red
        'header': '\033[92m',     # Green
        'highlight': '\033[7m'    # Reverse video
    }

def init_locale() -> None:
    """Initialize locale settings."""
    locale.setlocale(locale.LC_ALL, '')

def get_season(month: int) -> str:
    """Determine season for a given month with correct boundaries."""
    if 3 <= month <= 5: return 'spring'
    if 6 <= month <= 8: return 'summer'
    if 9 <= month <= 11: return 'autumn'
    return 'winter'

def colorize(text: str, *color_keys: str) -> str:
    """Apply ANSI color codes to text."""
    colors = ''.join(CalendarConfig.COLORS[key] for key in color_keys)
    return f"{colors}{text}{CalendarConfig.COLORS['reset']}"

def format_day(day: int, is_weekend: bool, is_today: bool) -> str:
    """Format a single day with appropriate coloring."""
    if day == 0:
        return '  '

    day_str = f"{day:2}"
    color = 'sunday' if is_weekend else 'weekday'

    if is_today:
        return colorize(day_str, 'highlight', color)
    return colorize(day_str, color)

def generate_weekdays_header() -> str:
    """Generate colored weekday abbreviations."""
    weekdays = (day[:2] for day in calendar.day_name)
    return ' '.join(
        colorize(day, 'sunday' if i == 6 else 'header')
        for i, day in enumerate(weekdays)
    )

def generate_month_title(month: int, month_name: str, year: int, show_year: bool) -> str:
    """Generate centered month title with proper seasonal coloring."""
    title = f"{month_name}{f' {year}' if show_year else ''}"
    return colorize(title.center(CalendarConfig.MONTH_WIDTH), get_season(month))

def generate_month_days(year: int, month: int, today: date) -> Generator[str, None, None]:
    """Generate formatted week lines for a month."""
    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdayscalendar(year, month):
        yield ' '.join(
            format_day(
                day=day,
                is_weekend=(i == 6),
                is_today=(day == today.day and month == today.month and year == today.year)
            )
            for i, day in enumerate(week)
        )

def render_month(year: int, month: int, today: date, show_year: bool = False) -> list[str]:
    """Render a complete month calendar."""
    month_name = calendar.month_name[month]
    lines = [
        generate_month_title(month, month_name, year, show_year),
        generate_weekdays_header()
    ]

    # Add weeks
    weeks = list(generate_month_days(year, month, today))
    lines.extend(weeks)

    # Pad to fixed number of weeks
    while len(lines) < CalendarConfig.WEEKS_TO_SHOW + 2:  # +2 for header and weekdays
        lines.append(' ' * CalendarConfig.MONTH_WIDTH)

    return lines

def render_quarter(months: Iterable[list[str]]) -> None:
    """Render a quarter (3 months) side by side."""
    for lines in zip(*months):
        print("  ".join(lines))

def render_year_header(year: int, num_months: int = 3) -> None:
    """Render centered year header for a group of months."""
    total_width = num_months * CalendarConfig.MONTH_WIDTH + (num_months - 1) * 2
    print(f"\n{colorize(str(year).center(total_width), get_season(1))}\n")

def render_year_view(year: int) -> None:
    """Render complete year view with proper seasonal colors."""
    today = date.today()
    render_year_header(year)

    # Group months by quarters
    for quarter_start in range(1, 13, 3):
        quarter_months = range(quarter_start, quarter_start + 3)
        months_data = [render_month(year, month, today) for month in quarter_months]
        render_quarter(months_data)
        print()

def render_three_month_view(today: date, year_above: bool = True) -> None:
    """Render previous/current/next month view with flexible year display."""
    months_data = []
    current_year = today.year

    if year_above:
        render_year_header(current_year)

    for offset in (-1, 0, 1):
        month = today.month + offset
        year = current_year
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        months_data.append(render_month(year, month, today, show_year=not year_above))

    render_quarter(months_data)

def cal(arg: Optional[Union[int, str]] = None, year: Optional[int] = None) -> None:
    """
    Display calendar views.

    Args:
        arg: None - current month
             3 - 3-month view
             month (1-12) - specific month (requires year)
             year - full year view
        year: Required if arg is month (1-12)
    """
    today = date.today()

    # Handle month+year case
    if isinstance(arg, int) and 1 <= arg <= 12 and year is not None:
        for line in render_month(year, arg, today, show_year=True):
            print(line)
        return

    # Original logic for other cases
    match arg:
        case None:
            for line in render_month(today.year, today.month, today, show_year=True):
                print(line)
        case 3:
            render_three_month_view(today)
        case str() | int() if str(arg).isdigit():
            render_year_view(int(arg))
        case _:
            print("Usage: cal() | cal(3) | cal(year) | cal(month, year)")


def main():
    """Command-line entry point that exactly matches cal()'s capabilities"""

    today = date.today()
    args = sys.argv[1:]

    usage = """
Usage:
  ppcal            Show current month
  ppcal 3          Show 3-month view (prev/current/next)
  ppcal 2024       Show full year view
  ppcal 6 2024     Show June 2024
  ppcal add        Add a new event
  ppcal del        Delete an event from today
"""

    if not args:
        cal()
        return

    if len(args) == 1:
        arg = args[0]
        if arg == '3':
            cal(3)
        elif arg.isdigit():
            if len(arg) == 4:
                cal(int(arg))  # Year view
            else:
                print(f"Missing year. Please use: ppcal {arg} YEAR\n{usage}")
        else:
            print(f"Invalid argument: {arg}\n{usage}")
        return

    if len(args) == 2:
        month, year = args
        if (month.isdigit() and year.isdigit() and
            1 <= int(month) <= 12 and
            len(year) == 4):
            cal(int(month), int(year))
            return

    print(f"Invalid arguments\n{usage}")
    sys.exit(1)

if __name__ == "__main__":
    main() 
