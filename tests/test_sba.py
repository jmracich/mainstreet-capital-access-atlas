import pandas as pd

from mainstreet_atlas.fetch import sba


def test_sba_aggregation_uses_latest_fiscal_year_and_county_lookup(tmp_path, monkeypatch):
    geography = pd.DataFrame(
        {
            "fips": ["17031", "22033"],
            "county_name": ["Cook County", "East Baton Rouge Parish"],
            "state_abbr": ["IL", "LA"],
        }
    )
    processed = tmp_path / "processed"
    processed.mkdir()
    geography.to_csv(processed / "county_geography.csv", index=False)
    monkeypatch.setattr(sba, "PROCESSED_DIR", processed)

    source = tmp_path / "sba.csv"
    pd.DataFrame(
        {
            "projectcounty": ["COOK", "COOK", "EAST BATON ROUGE"],
            "projectstate": ["IL", "IL", "LA"],
            "approvalfy": ["2025", "2026", "2026"],
            "grossapproval": ["100", "200", "300"],
        }
    ).to_csv(source, index=False)

    output = sba.aggregate_sba_county_lending([source], chunksize=2)

    assert output.to_dict(orient="records") == [
        {"fips": "17031", "sba_loan_count": 1, "sba_loan_amount": 200.0},
        {"fips": "22033", "sba_loan_count": 1, "sba_loan_amount": 300.0},
    ]
