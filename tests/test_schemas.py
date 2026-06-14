import pandas as pd
import pytest

from mainstreet_atlas.schemas import CountyRecord, validate_public_county_export


def test_county_record_validates_fips_digits():
    with pytest.raises(ValueError):
        CountyRecord(
            fips="17A31",
            county_name="Cook",
            state_abbr="IL",
            data_quality_grade="A",
        )


def test_county_record_accepts_valid_fips():
    record = CountyRecord(
        fips="17031",
        county_name="Cook",
        state_fips="17",
        state_abbr="IL",
        support_priority_signal=52.4,
        data_completeness=0.5,
        score_component_coverage=0.85,
        substantive_component_coverage=0.75,
        data_quality_grade="B",
    )

    assert record.fips == "17031"


def test_public_county_export_accepts_valid_records():
    frame = _valid_public_frame()

    validate_public_county_export(frame)


def test_public_county_export_rejects_duplicate_fips():
    frame = _valid_public_frame()
    frame.loc[1, "fips"] = "17031"

    with pytest.raises(ValueError, match="Duplicate county FIPS"):
        validate_public_county_export(frame)


def test_public_county_export_rejects_invalid_score_range():
    frame = _valid_public_frame()
    frame.loc[0, "support_priority_signal"] = 120

    with pytest.raises(ValueError, match="support_priority_signal outside"):
        validate_public_county_export(frame)


def test_public_county_export_rejects_missing_score_when_components_exist():
    frame = _valid_public_frame()
    frame.loc[0, "support_priority_signal"] = pd.NA

    with pytest.raises(ValueError, match="Missing Support Priority Signal"):
        validate_public_county_export(frame)


def test_public_county_export_rejects_grade_mismatch():
    frame = _valid_public_frame()
    frame.loc[0, "data_quality_grade"] = "A"

    with pytest.raises(ValueError, match="Data quality grade mismatches"):
        validate_public_county_export(frame)


def _valid_public_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fips": ["17031", "17113"],
            "county_name": ["Cook", "McLean"],
            "state_fips": ["17", "17"],
            "state_abbr": ["IL", "IL"],
            "state_name": ["Illinois", "Illinois"],
            "support_priority_signal": [52.4, 48.3],
            "small_business_importance": [61.0, 42.0],
            "capital_access_visibility_gap": [50.0, 45.0],
            "community_economic_stress": [55.0, 38.0],
            "housing_cost_pressure": [pd.NA, pd.NA],
            "local_support_ecosystem_gap": [49.0, 53.0],
            "data_completeness": [0.5, 0.5],
            "data_quality_gap": [50.0, 50.0],
            "data_quality_grade": ["C", "C"],
            "score_component_coverage": [0.85, 0.85],
            "substantive_component_coverage": [0.75, 0.75],
            "missing_source_fields": ["rent_burden_pct", "rent_burden_pct"],
        }
    )
