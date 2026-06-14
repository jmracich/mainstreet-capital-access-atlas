from zipfile import ZipFile

from mainstreet_atlas.fetch.ffiec_cra import (
    aggregate_cra_county_originations,
    parse_cra_aggregate_line,
)


def test_parse_cra_aggregate_line_reads_county_originations():
    line = (
        "A1-1 "
        "2024"
        "4"
        "1"
        "17"
        "031"
        "16980"
        "       "
        "N"
        "L"
        "   "
        "200"
        "0000000010"
        "0000000100"
        "0000000020"
        "0000000200"
        "0000000030"
        "0000000300"
        "0000000005"
        "0000000050"
        + (" " * 29)
    )

    assert parse_cra_aggregate_line(line) == {
        "fips": "17031",
        "cra_small_business_loans": 60,
        "cra_small_business_amount": 600000,
    }


def test_parse_cra_aggregate_line_ignores_non_county_totals():
    line = "A1-1 2024411703116980       NL   100" + ("0" * 80)

    assert parse_cra_aggregate_line(line) is None


def test_aggregate_cra_county_originations_reads_zip_members(tmp_path):
    line = (
        "A1-1 "
        "2024"
        "4"
        "1"
        "17"
        "031"
        "16980"
        "       "
        "N"
        "L"
        "   "
        "200"
        "0000000001"
        "0000000002"
        "0000000003"
        "0000000004"
        "0000000005"
        "0000000006"
        "0000000000"
        "0000000000"
        + (" " * 29)
    )
    path = tmp_path / "cra.zip"
    with ZipFile(path, "w") as archive:
        archive.writestr("aggregate.txt", f"{line}\n")

    output = aggregate_cra_county_originations(path)

    assert output.to_dict(orient="records") == [
        {
            "fips": "17031",
            "cra_small_business_loans": 9,
            "cra_small_business_amount": 12000,
        }
    ]
