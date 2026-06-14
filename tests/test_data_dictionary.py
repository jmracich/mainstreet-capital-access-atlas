import csv
from pathlib import Path

import pytest

from mainstreet_atlas.generate.data_dictionary import DICTIONARY_COLUMNS, dictionary_records


def test_data_dictionary_covers_generated_county_export():
    public_counties = Path("data/public/counties.csv")
    if not public_counties.exists():
        pytest.skip("Generated public county data is not present.")

    with public_counties.open(encoding="utf-8", newline="") as file:
        columns = next(csv.reader(file))

    records = dictionary_records(columns)

    assert [record["column_name"] for record in records] == columns
    assert all(set(record) == set(DICTIONARY_COLUMNS) for record in records)
    assert all(record["description"] for record in records)


def test_priority_dictionary_fields_are_generated_from_base_fields():
    records = dictionary_records(["poverty_pct_priority"])

    assert records[0]["column_name"] == "poverty_pct_priority"
    assert records[0]["category"] == "Normalized priority indicators"
    assert records[0]["used_in_signal"] is True
