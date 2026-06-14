"""Indicator display helpers."""

from __future__ import annotations

import math


def fmt_number(value: object, decimals: int = 0) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "Unavailable"
    if math.isnan(numeric):
        return "Unavailable"
    return f"{numeric:,.{decimals}f}"


def fmt_pct(value: object, decimals: int = 1) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "Unavailable"
    if math.isnan(numeric):
        return "Unavailable"
    return f"{numeric:.{decimals}f}%"
