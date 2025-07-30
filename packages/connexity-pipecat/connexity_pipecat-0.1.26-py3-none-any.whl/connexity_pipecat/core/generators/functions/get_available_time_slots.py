import json
from datetime import date, timedelta,datetime
import random
from typing import List, Any


def _next_business_dates(business_days=5, offset=3):
    dates = []
    current = date.today() + timedelta(days=offset)

    # If the starting day is a weekend, skip to next Monday
    while current.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        current += timedelta(days=1)

    while len(dates) < business_days:
        if current.weekday() < 5:
            dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


def _get_available_time_slots(dates: List[str]):
    time_slots = [
        "09:00 - 09:30", "09:30 - 10:00", "10:00 - 10:30", "10:30 - 11:00",
        "11:00 - 11:30", "11:30 - 12:00", "13:00 - 13:30", "13:30 - 14:00",
        "14:00 - 14:30", "14:30 - 15:00", "15:00 - 15:30", "15:30 - 16:00",
        "16:00 - 16:30", "16:30 - 17:00"
    ]

    result = []
    for date in dates:
        dt_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = f"{date}, {dt_obj.strftime('%A')}"

        if dt_obj.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
            free_slots = []
        else:
            random.seed(int(dt_obj.timestamp()))
            free_slots_count = random.randint(0, 7)
            free_slots = random.sample(time_slots, free_slots_count) if free_slots_count > 0 else []

        result.append({
            "date": formatted_date,
            "free_slots": sorted(free_slots)
        })

    return result


def get_available_time_slots_str(_: dict[str, Any] | None = None):
    next_5_business_days = _next_business_dates()
    slots = _get_available_time_slots(next_5_business_days)

    return json.dumps(slots, indent=4)