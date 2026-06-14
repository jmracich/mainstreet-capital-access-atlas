import pandas as pd

from mainstreet_atlas.transform.normalize import winsorized_percentile


def test_normalization_directionality_higher_priority():
    scores = winsorized_percentile(pd.Series([1, 2, 3, 4]), higher_is_priority=True)

    assert scores.iloc[-1] > scores.iloc[0]


def test_normalization_directionality_lower_priority():
    scores = winsorized_percentile(pd.Series([1, 2, 3, 4]), higher_is_priority=False)

    assert scores.iloc[0] > scores.iloc[-1]


def test_normalization_preserves_missing_values():
    scores = winsorized_percentile(pd.Series([1, None, 3]), higher_is_priority=True)

    assert scores.isna().iloc[1]
