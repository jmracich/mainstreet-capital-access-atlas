"""Manual BLS LAUS county unemployment import adapter."""

from __future__ import annotations

import logging

import pandas as pd

from mainstreet_atlas.fetch.common import source_record
from mainstreet_atlas.fetch.manual import prepare_manual_county_frame
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import MANUAL_DIR, PROCESSED_DIR

LOGGER = logging.getLogger(__name__)

MANUAL_PATH = MANUAL_DIR / "bls_laus_county.csv"
OUTPUT_PATH = PROCESSED_DIR / "bls_laus_county.csv"


def fetch(refresh: bool = False) -> dict:
    del refresh
    if MANUAL_PATH.exists():
        frame = pd.read_csv(MANUAL_PATH, dtype={"fips": str})
        prepared = prepare_laus_manual(frame)
        prepared.to_csv(OUTPUT_PATH, index=False)
        status = "available"
        local_path = OUTPUT_PATH
        fetched = True
    else:
        status = "manual_optional"
        local_path = None
        fetched = False
        LOGGER.info("No manual BLS LAUS file found at %s", MANUAL_PATH)

    record = source_record(
        source_id="bls_laus",
        dataset_name="BLS Local Area Unemployment Statistics county import",
        publisher="U.S. Bureau of Labor Statistics",
        access_method="Manual CSV adapter: data/manual/bls_laus_county.csv",
        url="https://www.bls.gov/lau/",
        status=status,
        coverage="County-level annual unemployment rate when a user-provided CSV is present",
        known_limitations=(
            "BLS LAUS is the preferred public source for local unemployment rates, but BLS bulk "
            "downloads may restrict automated retrieval. This adapter never fabricates values when "
            "the manual county file is absent."
        ),
        local_path=local_path,
        fetched=fetched,
    )
    upsert_source(record)
    return record


def prepare_laus_manual(frame: pd.DataFrame) -> pd.DataFrame:
    return prepare_manual_county_frame(
        frame,
        source_label="BLS LAUS",
        required_columns={"unemployment_pct"},
        optional_columns=["labor_force", "employed", "unemployed", "unemployment_year"],
    )
