"""Fetch Census SAIPE county poverty and income estimates."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import download_file, source_record
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import PROCESSED_DIR, RAW_DIR

LOGGER = logging.getLogger(__name__)


def saipe_workbook_url(year: int) -> str:
    short_year = str(year)[-2:]
    return (
        "https://www2.census.gov/programs-surveys/saipe/datasets/"
        f"{year}/{year}-state-and-county/est{short_year}all.xls"
    )


def fetch(settings: Settings, refresh: bool = False) -> dict:
    url = saipe_workbook_url(settings.saipe_year)
    raw_path = RAW_DIR / f"est{str(settings.saipe_year)[-2:]}all.xls"
    output_path = PROCESSED_DIR / "saipe_county.csv"
    downloaded = download_file(url, raw_path, settings, refresh=refresh)

    frame = _read_saipe_workbook(raw_path, settings.saipe_year)
    frame.to_csv(output_path, index=False)
    LOGGER.info("Wrote %s SAIPE county rows", len(frame))

    record = source_record(
        source_id="census_saipe",
        dataset_name=f"{settings.saipe_year} Small Area Income and Poverty Estimates",
        publisher="U.S. Census Bureau Small Area Income and Poverty Estimates Program",
        access_method="Automated download of official all-counties Excel workbook",
        url="https://www.census.gov/data/datasets/2024/demo/saipe/2024-state-and-county.html",
        status="available",
        coverage="County-level income and poverty estimates for states and the District of Columbia",
        known_limitations=(
            "SAIPE estimates are model-based and designed for federal program administration. They "
            "are useful economic context but do not replace local verification or ACS detail."
        ),
        local_path=output_path,
        fetched=downloaded or output_path.exists(),
    )
    upsert_source(record)
    return record


def _read_saipe_workbook(path: Path, year: int) -> pd.DataFrame:
    raw = pd.read_excel(
        path,
        sheet_name=0,
        header=3,
        dtype={"State FIPS Code": str, "County FIPS Code": str},
        na_values=["."],
    )
    return _parse_saipe_frame(raw, year)


def _parse_saipe_frame(raw: pd.DataFrame, year: int) -> pd.DataFrame:
    counties = raw[raw["County FIPS Code"].astype(str).str.zfill(3) != "000"].copy()
    output = pd.DataFrame()
    output["fips"] = (
        counties["State FIPS Code"].astype(str).str.zfill(2)
        + counties["County FIPS Code"].astype(str).str.zfill(3)
    )
    output["saipe_poverty_count"] = _numeric(counties["Poverty Estimate, All Ages"])
    output["saipe_poverty_pct"] = _numeric(counties["Poverty Percent, All Ages"])
    output["saipe_median_household_income"] = _numeric(counties["Median Household Income"])
    output["income_poverty_estimate_year"] = year
    return output


def _numeric(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce")
