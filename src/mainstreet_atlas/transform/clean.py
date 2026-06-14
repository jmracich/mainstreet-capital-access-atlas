"""Data cleaning helpers."""

from __future__ import annotations

import pandas as pd


def ensure_fips(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    if isinstance(numerator, pd.Series):
        index = numerator.index
    elif isinstance(denominator, pd.Series):
        index = denominator.index
    else:
        index = pd.RangeIndex(1)
    numerator_series = numerator if isinstance(numerator, pd.Series) else pd.Series(numerator, index=index)
    denominator_series = (
        denominator if isinstance(denominator, pd.Series) else pd.Series(denominator, index=index)
    )
    numerator_series = numerator_series.reindex(index)
    denominator_series = denominator_series.reindex(index)
    denominator_series = denominator_series.where(denominator_series != 0)
    return numerator_series / denominator_series


def numeric_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    output = frame.copy()
    for column in columns:
        if column in output.columns:
            output[column] = pd.to_numeric(output[column], errors="coerce")
    return output
