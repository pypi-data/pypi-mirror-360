from datetime import timedelta, datetime
from typing import Any


def _get_day_suffix(day):
    if 11 <= day % 100 <= 13:
        return "th"
    last_digit = day % 10
    if last_digit == 1:
        return "st"
    elif last_digit == 2:
        return "nd"
    elif last_digit == 3:
        return "rd"
    else:
        return "th"


def get_grouped_calendar(_: dict[str, Any] | None = None, start_date=None):
    if not start_date:
        start_date = datetime.now()

    calendar_groups = {}

    for i in range(31):
        current_date = start_date + timedelta(days=i)
        suffix = _get_day_suffix(current_date.day)
        weekday = current_date.strftime("%A")
        date_str = f"{current_date.day}{suffix} - {weekday}"
        key = (current_date.month, current_date.year)
        if key not in calendar_groups:
            calendar_groups[key] = []
        calendar_groups[key].append(date_str)

    output = ""

    for month, year in sorted(calendar_groups):
        header = f"Calendar for {datetime(year, month, 1).strftime('%B %Y')}:"
        output += f"\n{header}\n\n"
        output += "\n".join(calendar_groups[(month, year)])
        output += "\n"
    return output.strip()