"""Small helpers for generated chart data."""

from __future__ import annotations

import pandas as pd


def score_band_counts(frame: pd.DataFrame) -> list[dict[str, int | str]]:
    bins = [0, 25, 50, 75, 100]
    labels = ["0-25", "26-50", "51-75", "76-100"]
    series = pd.cut(frame["support_priority_signal"], bins=bins, labels=labels, include_lowest=True)
    counts = series.value_counts().reindex(labels, fill_value=0)
    return [{"band": str(label), "count": int(count)} for label, count in counts.items()]
