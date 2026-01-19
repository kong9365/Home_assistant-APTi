"""Helper functions for APT.i integration."""

from __future__ import annotations

import re
from typing import Any

from .const import LOGGER


def is_phone_number(id_value: str) -> bool:
    """Check if a string is in phone number format (010 followed by 8 digits)."""
    phone_number_pattern = r"^0\d{9,10}$"
    return bool(re.match(phone_number_pattern, id_value.replace("-", "")))


def parse_amount(value: str | int | None) -> int | None:
    """Parse amount string to integer."""
    if value is None:
        return None

    if isinstance(value, int):
        return value

    try:
        cleaned = str(value).replace(",", "").replace("원", "").strip()
        return int(cleaned)
    except (ValueError, TypeError):
        LOGGER.warning("금액 파싱 실패: %s", value)
        return None


def format_amount(value: int | None) -> str:
    """Format integer amount with commas and won symbol."""
    if value is None:
        return "0원"
    return f"{value:,}원"
