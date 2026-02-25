"""
General-purpose helper functions for the Engagement Tracker.

These utilities are:
- pure (no side effects)
- easy to test
- reusable across UI and query layers
"""

import re
from typing import Optional


# ---------------------------------------------------------
# STRING CLEANING
# ---------------------------------------------------------

def clean_text(value: Optional[str]) -> str:
    """
    Normalize text fields by stripping whitespace and converting
    None/NaN-like values into empty strings.
    """
    if value is None:
        return ""
    return str(value).strip()


def normalize_website(url: str) -> str:
    """
    Ensure websites have a consistent format.
    """
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


# ---------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------

def is_valid_year(value: str) -> bool:
    """
    Validate that a year is a 4-digit number between 1800 and 2100.
    """
    if not value:
        return False
    if not re.fullmatch(r"\d{4}", value):
        return False
    year = int(value)
    return 1800 <= year <= 2100


def is_valid_id(value) -> bool:
    """
    Validate that an ID is a positive integer.
    """
    try:
        return int(value) > 0
    except Exception:
        return False


# ---------------------------------------------------------
# DISPLAY HELPERS
# ---------------------------------------------------------

def format_count(n: int) -> str:
    """
    Format integers with commas for readability.
    """
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)