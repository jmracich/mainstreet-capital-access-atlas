import pandas as pd
import pytest

from mainstreet_atlas.fetch.census_cbp import _parse_cbp_frame


def test_cbp_parser_outputs_business_mix_and_top_industry():
    raw = pd.DataFrame(
        [
            {
                "fipstate": "17",
                "fipscty": "031",
                "naics": "------",
                "emp": "1000",
                "ap": "50000",
                "est": "100",
                "n<5": "40",
                "n5_9": "20",
                "n10_19": "10",
            },
            {
                "fipstate": "17",
                "fipscty": "031",
                "naics": "44----",
                "emp": "300",
                "ap": "10000",
                "est": "30",
                "n<5": "10",
                "n5_9": "5",
                "n10_19": "3",
            },
            {
                "fipstate": "17",
                "fipscty": "031",
                "naics": "62----",
                "emp": "500",
                "ap": "20000",
                "est": "35",
                "n<5": "12",
                "n5_9": "8",
                "n10_19": "4",
            },
        ]
    )

    frame = _parse_cbp_frame(raw)
    row = frame.iloc[0].to_dict()

    assert row["fips"] == "17031"
    assert row["establishments"] == 100
    assert row["business_employment"] == 1000
    assert row["annual_payroll_thousands"] == 50000
    assert row["small_establishments_under_20"] == 70
    assert row["small_establishments_under_20_pct"] == pytest.approx(70.0)
    assert row["top_industry_naics2"] == "62"
    assert row["top_industry_name"] == "Health care and social assistance"
    assert row["top_industry_establishments"] == 35
    assert row["top_industry_establishment_share"] == pytest.approx(35.0)
