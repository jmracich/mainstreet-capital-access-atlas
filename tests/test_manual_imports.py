import pandas as pd
import pytest

from mainstreet_atlas.fetch.manual import prepare_manual_county_frame


def test_manual_import_rejects_unsupported_columns():
    frame = pd.DataFrame(
        {
            "fips": ["17031"],
            "sba_loan_count": [12],
            "borrower_name": ["Do not publish"],
        }
    )

    with pytest.raises(ValueError, match="unsupported columns"):
        prepare_manual_county_frame(
            frame,
            source_label="SBA",
            required_columns={"sba_loan_count"},
            optional_columns=[],
        )


def test_manual_import_rejects_duplicate_fips():
    frame = pd.DataFrame({"fips": ["17031", "17031"], "cdfi_count": [2, 3]})

    with pytest.raises(ValueError, match="duplicate county FIPS"):
        prepare_manual_county_frame(
            frame,
            source_label="CDFI",
            required_columns={"cdfi_count"},
            optional_columns=[],
        )


def test_manual_import_rejects_invalid_fips():
    frame = pd.DataFrame({"fips": ["17A31"], "cdfi_count": [2]})

    with pytest.raises(ValueError, match="invalid five-digit county FIPS"):
        prepare_manual_county_frame(
            frame,
            source_label="CDFI",
            required_columns={"cdfi_count"},
            optional_columns=[],
        )


def test_manual_import_rejects_nonnumeric_measure_values():
    frame = pd.DataFrame({"fips": ["17031"], "cdfi_count": ["many"]})

    with pytest.raises(ValueError, match="nonnumeric values"):
        prepare_manual_county_frame(
            frame,
            source_label="CDFI",
            required_columns={"cdfi_count"},
            optional_columns=[],
        )
