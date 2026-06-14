"""Normalization helpers with explicit directionality."""

from __future__ import annotations

import numpy as np
import pandas as pd


def winsorized_percentile(
    values: pd.Series,
    *,
    higher_is_priority: bool,
    lower_quantile: float = 0.05,
    upper_quantile: float = 0.95,
) -> pd.Series:
    """Return 0-100 percentile scores while preserving missing values."""

    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().sum() == 0:
        return pd.Series(np.nan, index=values.index)

    lower = numeric.quantile(lower_quantile)
    upper = numeric.quantile(upper_quantile)
    clipped = numeric.clip(lower=lower, upper=upper)
    percentiles = clipped.rank(pct=True, method="average") * 100
    if not higher_is_priority:
        percentiles = 100 - percentiles
    return percentiles.where(numeric.notna())


def row_mean(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    existing = [column for column in columns if column in frame.columns]
    if not existing:
        return pd.Series(np.nan, index=frame.index)
    return frame[existing].mean(axis=1, skipna=True)
