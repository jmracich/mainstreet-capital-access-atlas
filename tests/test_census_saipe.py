import pandas as pd

from mainstreet_atlas.fetch.census_saipe import _parse_saipe_frame


def test_saipe_parser_outputs_county_income_and_poverty():
    raw = pd.DataFrame(
        [
            {
                "State FIPS Code": "17",
                "County FIPS Code": "000",
                "Poverty Estimate, All Ages": 1434871,
                "Poverty Percent, All Ages": 11.5,
                "Median Household Income": 83327,
            },
            {
                "State FIPS Code": "17",
                "County FIPS Code": "001",
                "Poverty Estimate, All Ages": 8293,
                "Poverty Percent, All Ages": 13.3,
                "Median Household Income": 68432,
            },
        ]
    )

    frame = _parse_saipe_frame(raw, 2024)

    assert frame.to_dict(orient="records") == [
        {
            "fips": "17001",
            "saipe_poverty_count": 8293.0,
            "saipe_poverty_pct": 13.3,
            "saipe_median_household_income": 68432.0,
            "income_poverty_estimate_year": 2024,
        }
    ]
