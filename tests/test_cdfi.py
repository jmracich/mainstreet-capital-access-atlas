import pandas as pd

from mainstreet_atlas.fetch.cdfi import aggregate_certified_cdfis


def test_cdfi_aggregation_assigns_zip_to_primary_county(tmp_path):
    workbook = tmp_path / "cdfi.xlsx"
    crosswalk = tmp_path / "crosswalk.txt"

    rows = [
        ["note", None, None],
        ["Organization Name", "Zipcode", "State"],
        ["CDFI One", "60601--100", "IL"],
        ["CDFI Two", "60601", "IL"],
        ["CDFI Three", "10002", "NY"],
    ]
    pd.DataFrame(rows).to_excel(
        workbook,
        sheet_name="List of Certified CDFIs",
        header=False,
        index=False,
    )
    pd.DataFrame(
        {
            "GEOID_ZCTA5_20": ["60601", "60601", "10002"],
            "GEOID_COUNTY_20": ["17031", "17043", "36061"],
            "AREALAND_PART": ["90", "10", "50"],
            "AREAWATER_PART": ["0", "0", "0"],
        }
    ).to_csv(crosswalk, sep="|", index=False)

    output = aggregate_certified_cdfis(workbook, crosswalk)

    assert output.to_dict(orient="records") == [
        {"fips": "17031", "cdfi_count": 2},
        {"fips": "36061", "cdfi_count": 1},
    ]
