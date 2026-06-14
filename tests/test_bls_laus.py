import pandas as pd
import pytest

from mainstreet_atlas.fetch.bls_laus import prepare_laus_manual


def test_prepare_laus_manual_normalizes_required_fields():
    frame = pd.DataFrame(
        {
            "fips": [17031],
            "unemployment_pct": ["5.1"],
            "labor_force": ["2600000"],
            "employed": ["2467400"],
            "unemployed": ["132600"],
            "unemployment_year": ["2024"],
        }
    )

    prepared = prepare_laus_manual(frame)

    assert prepared.to_dict(orient="records") == [
        {
            "fips": "17031",
            "unemployment_pct": 5.1,
            "labor_force": 2600000,
            "employed": 2467400,
            "unemployed": 132600,
            "unemployment_year": 2024,
        }
    ]


def test_prepare_laus_manual_requires_unemployment_rate():
    with pytest.raises(ValueError, match="unemployment_pct"):
        prepare_laus_manual(pd.DataFrame({"fips": ["17031"]}))
