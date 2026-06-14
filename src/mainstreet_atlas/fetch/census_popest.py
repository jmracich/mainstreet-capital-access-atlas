"""Fetch Census county population estimates from public CSV files."""

from __future__ import annotations

import logging

import pandas as pd

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import download_file, source_record
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import PROCESSED_DIR, RAW_DIR

LOGGER = logging.getLogger(__name__)


def popest_csv_url(year: int) -> str:
    return (
        "https://www2.census.gov/programs-surveys/popest/datasets/"
        f"2020-{year}/counties/totals/co-est{year}-alldata.csv"
    )


def fetch(settings: Settings, refresh: bool = False) -> dict:
    url = popest_csv_url(settings.popest_year)
    raw_path = RAW_DIR / f"co-est{settings.popest_year}-alldata.csv"
    output_path = PROCESSED_DIR / "population_estimates_county.csv"
    fetched = download_file(url, raw_path, settings, refresh=refresh)

    frame = _read_population_file(raw_path, settings.popest_year)
    frame.to_csv(output_path, index=False)
    LOGGER.info("Wrote %s Census population estimate county rows", len(frame))

    record = source_record(
        source_id="census_popest",
        dataset_name=f"Vintage {settings.popest_year} County Population Estimates",
        publisher="U.S. Census Bureau Population Estimates Program",
        access_method="Automated download of official county population estimates CSV",
        url=url,
        status="available",
        coverage="County-level resident population estimates for counties and county equivalents",
        known_limitations=(
            "Population estimates are revised by vintage and use boundaries from the estimate series. "
            "They provide denominator context but do not measure household stress or local resources."
        ),
        local_path=output_path,
        fetched=fetched or output_path.exists(),
    )
    upsert_source(record)
    return record


def _read_population_file(path, year: int) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype={"STATE": str, "COUNTY": str}, encoding="latin1")
    counties = raw[(raw["SUMLEV"].astype(str) == "50") & (raw["COUNTY"].astype(str) != "000")].copy()
    estimate_column = f"POPESTIMATE{year}"
    if estimate_column not in counties.columns:
        msg = f"Population estimates file is missing {estimate_column}"
        raise ValueError(msg)

    output = pd.DataFrame()
    output["fips"] = counties["STATE"].astype(str).str.zfill(2) + counties["COUNTY"].astype(str).str.zfill(3)
    output["population"] = pd.to_numeric(counties[estimate_column], errors="coerce")
    output["population_estimate_year"] = year
    output["population_estimates_base_2020"] = pd.to_numeric(
        counties.get("ESTIMATESBASE2020"),
        errors="coerce",
    )
    return output
