import re


def is_valid_iso_language(lang_code: str) -> bool:
    """Check if lang_code is a two-letter, lowercase language code."""
    pattern = r"^[a-z]{2}$"
    return bool(re.match(pattern, lang_code))


def is_valid_end_call_time(seconds: int | None):

    if not seconds or seconds >= 60:
        return True

    return False
