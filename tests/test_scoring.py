import pandas as pd

from mainstreet_atlas.transform.scoring import data_quality_grade, score_counties


def test_score_range_and_missing_values_do_not_crash():
    frame = pd.DataFrame(
        {
            "fips": ["17031", "17113", "17019"],
            "county_name": ["Cook", "McLean", "Champaign"],
            "state_abbr": ["IL", "IL", "IL"],
            "establishments": [120000, 5000, None],
            "business_employment": [2500000, 80000, 70000],
            "population": [5200000, 170000, 210000],
            "branch_count": [550, 35, 31],
            "poverty_pct": [14.0, None, 18.0],
            "unemployment_pct": [5.0, 3.5, None],
        }
    )

    scored = score_counties(frame)

    assert scored["support_priority_signal"].between(0, 100).all()
    assert set(scored["data_quality_grade"]).issubset({"A", "B", "C", "D"})


def test_data_quality_grade_thresholds():
    assert data_quality_grade(0.9) == "A"
    assert data_quality_grade(0.7) == "B"
    assert data_quality_grade(0.5) == "C"
    assert data_quality_grade(0.2) == "D"


def test_no_substantive_data_has_unavailable_score():
    frame = pd.DataFrame(
        {
            "fips": ["60010"],
            "county_name": ["Eastern"],
            "state_abbr": ["AS"],
        }
    )

    scored = score_counties(frame)

    assert scored["support_priority_signal"].isna().all()
