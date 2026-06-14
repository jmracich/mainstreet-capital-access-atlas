from pathlib import Path

from mainstreet_atlas.fetch.census_popest import _read_population_file


def test_population_estimates_parser_outputs_county_population(tmp_path: Path):
    source = tmp_path / "co-est2025-alldata.csv"
    source.write_text(
        "\n".join(
            [
                "SUMLEV,STATE,COUNTY,STNAME,CTYNAME,ESTIMATESBASE2020,POPESTIMATE2025",
                "040,01,000,Alabama,Alabama,5025369,5157699",
                "050,01,001,Alabama,Autauga County,58805,61920",
            ]
        ),
        encoding="latin1",
    )

    frame = _read_population_file(source, 2025)

    assert frame.to_dict(orient="records") == [
        {
            "fips": "01001",
            "population": 61920,
            "population_estimate_year": 2025,
            "population_estimates_base_2020": 58805,
        }
    ]
