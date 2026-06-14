import pandas as pd

from mainstreet_atlas.fetch.fdic import _aggregate_sod_to_fips


def test_fdic_sod_aggregates_branch_deposits_to_county():
    raw = pd.DataFrame(
        [
            {"YEAR": "2025", "STCNTY": "17031", "DEPSUMBR": "100"},
            {"YEAR": "2025", "STCNTY": "17031", "DEPSUMBR": "250"},
            {"YEAR": "2025", "STCNTY": "17043", "DEPSUMBR": "50"},
        ]
    )

    frame = _aggregate_sod_to_fips(raw).sort_values("fips").reset_index(drop=True)

    assert frame.to_dict(orient="records") == [
        {
            "fips": "17031",
            "sod_year": 2025,
            "sod_branch_records": 2,
            "branch_deposits_thousands": 350,
        },
        {
            "fips": "17043",
            "sod_year": 2025,
            "sod_branch_records": 1,
            "branch_deposits_thousands": 50,
        },
    ]
