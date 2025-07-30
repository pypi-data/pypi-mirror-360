from datetime import datetime
from typing import Any


def current_timestamp(_: dict[str, Any] | None = None) -> str:
    return datetime.now().strftime("%Y-%m-%d, %A. Time: %H:%M.")
