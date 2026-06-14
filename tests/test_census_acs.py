import pytest

from mainstreet_atlas.fetch.census_acs import _transform_acs_rows


def test_acs_transform_outputs_public_household_and_education_context():
    frame = _transform_acs_rows(
        [
            {
                "NAME": "Cook County, Illinois",
                "state": "17",
                "county": "031",
                "B01003_001E": "1000",
                "B11001_001E": "400",
                "B19013_001E": "60000",
                "B17001_001E": "1000",
                "B17001_002E": "120",
                "B23025_003E": "500",
                "B23025_005E": "25",
                "B25070_001E": "200",
                "B25070_007E": "20",
                "B25070_008E": "15",
                "B25070_009E": "10",
                "B25070_010E": "5",
                "B08201_001E": "400",
                "B08201_002E": "40",
                "B28002_001E": "400",
                "B28002_013E": "80",
                "B15003_001E": "600",
                "B15003_022E": "100",
                "B15003_023E": "50",
                "B15003_024E": "10",
                "B15003_025E": "5",
            }
        ]
    )

    row = frame.iloc[0].to_dict()

    assert row["fips"] == "17031"
    assert row["households"] == 400
    assert row["poverty_pct"] == pytest.approx(12.0)
    assert row["unemployment_pct"] == pytest.approx(5.0)
    assert row["rent_burden_pct"] == pytest.approx(25.0)
    assert row["no_vehicle_pct"] == pytest.approx(10.0)
    assert row["no_internet_pct"] == pytest.approx(20.0)
    assert row["education_population_25_plus"] == 600
    assert row["bachelors_or_higher_population"] == 165
    assert row["bachelors_or_higher_pct"] == pytest.approx(27.5)
    assert "poverty_universe" not in frame.columns
    assert "rent_50_plus" not in frame.columns
