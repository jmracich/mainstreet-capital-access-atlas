"""Fetch Census County Business Patterns from downloadable public files."""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path

import pandas as pd

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import download_file, source_record
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import PROCESSED_DIR, RAW_DIR

LOGGER = logging.getLogger(__name__)

NAICS_SECTOR_NAMES = {
    "11": "Agriculture, forestry, fishing and hunting",
    "21": "Mining, quarrying, and oil and gas extraction",
    "22": "Utilities",
    "23": "Construction",
    "31": "Manufacturing",
    "32": "Manufacturing",
    "33": "Manufacturing",
    "42": "Wholesale trade",
    "44": "Retail trade",
    "45": "Retail trade",
    "48": "Transportation and warehousing",
    "49": "Transportation and warehousing",
    "51": "Information",
    "52": "Finance and insurance",
    "53": "Real estate and rental and leasing",
    "54": "Professional, scientific, and technical services",
    "55": "Management of companies and enterprises",
    "56": "Administrative and support and waste management services",
    "61": "Educational services",
    "62": "Health care and social assistance",
    "71": "Arts, entertainment, and recreation",
    "72": "Accommodation and food services",
    "81": "Other services except public administration",
    "92": "Public administration",
}


def cbp_zip_url(year: int) -> str:
    short_year = str(year)[-2:]
    return f"https://www2.census.gov/programs-surveys/cbp/datasets/{year}/cbp{short_year}co.zip"


def fetch(settings: Settings, refresh: bool = False) -> dict:
    url = cbp_zip_url(settings.cbp_year)
    zip_path = RAW_DIR / f"cbp{str(settings.cbp_year)[-2:]}co.zip"
    output_path = PROCESSED_DIR / "cbp_county.csv"
    fetched = download_file(url, zip_path, settings, refresh=refresh)

    frame = _read_cbp_zip(zip_path)
    frame.to_csv(output_path, index=False)
    LOGGER.info("Wrote %s CBP county rows", len(frame))

    record = source_record(
        source_id="census_cbp",
        dataset_name=f"{settings.cbp_year} County Business Patterns",
        publisher="U.S. Census Bureau",
        access_method="Automated download of official County Business Patterns county file",
        url=url,
        status="available",
        coverage="County-level establishments, employment, and annual payroll where reported by CBP",
        known_limitations=(
            "CBP covers establishments with paid employees. Some employment/payroll cells may be "
            "suppressed or noise-infused under Census disclosure rules."
        ),
        local_path=output_path,
        fetched=fetched or output_path.exists(),
    )
    upsert_source(record)
    return record


def _read_cbp_zip(zip_path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith((".csv", ".txt"))]
        if not names:
            msg = f"No CSV/TXT member found in {zip_path}"
            raise FileNotFoundError(msg)
        with archive.open(names[0]) as file:
            raw = pd.read_csv(file, dtype=str, encoding="latin1")

    return _parse_cbp_frame(raw)


def _parse_cbp_frame(raw: pd.DataFrame) -> pd.DataFrame:
    raw.columns = [column.strip().lower() for column in raw.columns]
    naics_col = _first_existing(raw, ["naics", "naics2017", "naics2022"])
    state_col = _first_existing(raw, ["fipstate", "state", "statefp"])
    county_col = _first_existing(raw, ["fipscty", "county", "countyfp"])
    if not state_col or not county_col:
        msg = "CBP file did not contain state/county FIPS columns"
        raise ValueError(msg)
    if not naics_col:
        msg = "CBP file did not contain a NAICS column"
        raise ValueError(msg)

    raw = raw.copy()
    raw["fips"] = (
        raw[state_col].astype(str).str.zfill(2) + raw[county_col].astype(str).str.zfill(3)
    )
    raw["naics_clean"] = raw[naics_col].astype(str).str.strip()

    total = _parse_total_rows(raw)
    top_sector = _parse_top_industry_rows(raw)
    output = total.merge(top_sector, on="fips", how="left")
    output["top_industry_establishment_share"] = (
        output["top_industry_establishments"] / output["establishments"].where(output["establishments"] != 0)
    ) * 100
    output["small_establishments_under_20_pct"] = (
        output["small_establishments_under_20"] / output["establishments"].where(output["establishments"] != 0)
    ) * 100
    return output


def _parse_total_rows(raw: pd.DataFrame) -> pd.DataFrame:
    total_mask = raw["naics_clean"].isin(["00", "000000", "------", "0", "Total for all sectors"])
    total = raw[total_mask].copy() if total_mask.any() else raw.copy()

    output = pd.DataFrame()
    output["fips"] = total["fips"]
    output["establishments"] = _numeric(total, _first_existing(total, ["est", "estab", "establishments"]))
    output["business_employment"] = _numeric(total, _first_existing(total, ["emp", "employment"]))
    output["annual_payroll_thousands"] = _numeric(total, _first_existing(total, ["ap", "payann"]))
    small_columns = [_first_existing(total, [name]) for name in ["n<5", "n5_9", "n10_19"]]
    small_columns = [column for column in small_columns if column]
    if small_columns:
        small_frame = total[small_columns].apply(pd.to_numeric, errors="coerce")
        output["small_establishments_under_20"] = small_frame.sum(axis=1, min_count=1)
    else:
        output["small_establishments_under_20"] = pd.NA
    return output.groupby("fips", as_index=False).sum(numeric_only=True, min_count=1)


def _parse_top_industry_rows(raw: pd.DataFrame) -> pd.DataFrame:
    sector_mask = raw["naics_clean"].str.fullmatch(r"\d{2}----", na=False)
    sectors = raw[sector_mask].copy()
    if sectors.empty:
        return pd.DataFrame(
            columns=["fips", "top_industry_naics2", "top_industry_name", "top_industry_establishments"]
        )

    sectors["top_industry_naics2"] = sectors["naics_clean"].str[:2]
    sectors["top_industry_name"] = sectors["top_industry_naics2"].map(NAICS_SECTOR_NAMES)
    sectors["top_industry_establishments"] = _numeric(
        sectors,
        _first_existing(sectors, ["est", "estab", "establishments"]),
    )
    sectors = sectors.dropna(subset=["top_industry_establishments"])
    if sectors.empty:
        return pd.DataFrame(
            columns=["fips", "top_industry_naics2", "top_industry_name", "top_industry_establishments"]
        )
    sectors = sectors.sort_values(
        ["fips", "top_industry_establishments", "top_industry_naics2"],
        ascending=[True, False, True],
    )
    return sectors.groupby("fips", as_index=False).first()[
        ["fips", "top_industry_naics2", "top_industry_name", "top_industry_establishments"]
    ]


def _first_existing(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    return None


def _numeric(frame: pd.DataFrame, column: str | None) -> pd.Series:
    if column is None:
        return pd.Series([pd.NA] * len(frame), dtype="Float64")
    return pd.to_numeric(frame[column], errors="coerce")
