"""Automated certified CDFI county aggregation adapter."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from requests import RequestException

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import download_file, request_session, source_record
from mainstreet_atlas.fetch.manual import prepare_manual_county_frame
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import MANUAL_DIR, PROCESSED_DIR, RAW_DIR

LOGGER = logging.getLogger(__name__)

MANUAL_PATH = MANUAL_DIR / "cdfi_county.csv"
OUTPUT_PATH = PROCESSED_DIR / "cdfi_county.csv"
CERTIFICATION_PAGE_URL = "https://www.cdfifund.gov/programs-training/certification/cdfi"
ZCTA_COUNTY_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/"
    "tab20_zcta520_county20_natl.txt"
)


def fetch(settings: Settings, refresh: bool = False) -> dict:
    try:
        workbook_url = _current_cdfi_workbook_url(settings)
        workbook_path = RAW_DIR / "cdfi_current_certified.xlsx"
        crosswalk_path = RAW_DIR / "census_zcta_county_2020.txt"
        download_file(workbook_url, workbook_path, settings, refresh=refresh)
        download_file(ZCTA_COUNTY_URL, crosswalk_path, settings, refresh=refresh)
        frame = aggregate_certified_cdfis(workbook_path, crosswalk_path)
        if frame.empty:
            raise ValueError("Certified CDFI workbook did not produce county-level rows")
        frame.to_csv(OUTPUT_PATH, index=False)
        status = "available"
        local_path = OUTPUT_PATH
        fetched = True
    except (RequestException, ValueError, OSError, ImportError) as exc:
        LOGGER.warning("Automated CDFI fetch unavailable: %s", exc)
        if not MANUAL_PATH.exists():
            status = "unavailable"
            local_path = None
            fetched = False
        else:
            LOGGER.info("Falling back to manual CDFI file at %s", MANUAL_PATH)
            _prepare_manual_file()
            status = "available"
            local_path = OUTPUT_PATH
            fetched = True

    record = source_record(
        source_id="cdfi",
        dataset_name="Certified CDFI county aggregate",
        publisher="Community Development Financial Institutions Fund",
        access_method="Automated CDFI Fund certified list plus Census ZCTA-county relationship file",
        url=CERTIFICATION_PAGE_URL,
        status=status,
        coverage="County-level certified CDFI headquarters count from public certified CDFI list",
        known_limitations=(
            "CDFI headquarters counts do not measure service areas, lending volume, or relationship "
            "strength. ZIP-to-county assignment uses the largest 2020 Census ZCTA-county land/water overlap."
        ),
        local_path=local_path,
        fetched=fetched,
    )
    upsert_source(record)
    return record


def _prepare_manual_file() -> None:
    frame = pd.read_csv(MANUAL_PATH, dtype={"fips": str})
    frame = prepare_manual_county_frame(
        frame,
        source_label="CDFI",
        required_columns={"cdfi_count"},
        optional_columns=[],
    )
    frame.to_csv(OUTPUT_PATH, index=False)


def _current_cdfi_workbook_url(settings: Settings) -> str:
    session = request_session(settings)
    response = session.get(CERTIFICATION_PAGE_URL, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    match = re.search(
        r'href="([^"]+)"[^>]*>\s*List of Currently Certified CDFIs',
        response.text,
        flags=re.IGNORECASE,
    )
    if not match:
        raise ValueError("Current certified CDFI workbook link was not found")
    return urljoin(CERTIFICATION_PAGE_URL, match.group(1))


def aggregate_certified_cdfis(workbook_path: Path, crosswalk_path: Path) -> pd.DataFrame:
    cdfis = _read_certified_cdfis(workbook_path)
    zip_to_county = _zip_to_primary_county(crosswalk_path)
    cdfis["fips"] = cdfis["zip"].map(zip_to_county)
    output = (
        cdfis.dropna(subset=["fips"])
        .groupby("fips", as_index=False)
        .size()
        .rename(columns={"size": "cdfi_count"})
    )
    output["fips"] = output["fips"].astype(str).str.zfill(5)
    output["cdfi_count"] = output["cdfi_count"].astype(int)
    return output.sort_values("fips").reset_index(drop=True)


def _read_certified_cdfis(path: Path) -> pd.DataFrame:
    preview = pd.read_excel(path, sheet_name="List of Certified CDFIs", header=None)
    header_matches = preview.index[preview.eq("Organization Name").any(axis=1)].tolist()
    if not header_matches:
        raise ValueError("Certified CDFI workbook header row was not found")

    frame = pd.read_excel(path, sheet_name="List of Certified CDFIs", header=header_matches[0])
    if "Zipcode" not in frame.columns:
        raise ValueError("Certified CDFI workbook is missing Zipcode column")
    output = pd.DataFrame({"zip": frame["Zipcode"].map(_normalize_zip)})
    return output.dropna(subset=["zip"])


def _zip_to_primary_county(path: Path) -> dict[str, str]:
    crosswalk = pd.read_csv(path, sep="|", dtype=str, encoding="utf-8-sig")
    required = {"GEOID_ZCTA5_20", "GEOID_COUNTY_20", "AREALAND_PART", "AREAWATER_PART"}
    missing = required - set(crosswalk.columns)
    if missing:
        raise ValueError(f"Census ZCTA-county crosswalk missing columns: {', '.join(sorted(missing))}")

    crosswalk = crosswalk.dropna(subset=["GEOID_ZCTA5_20", "GEOID_COUNTY_20"]).copy()
    crosswalk["overlap_area"] = (
        pd.to_numeric(crosswalk["AREALAND_PART"], errors="coerce").fillna(0)
        + pd.to_numeric(crosswalk["AREAWATER_PART"], errors="coerce").fillna(0)
    )
    primary = crosswalk.sort_values("overlap_area", ascending=False).drop_duplicates(
        "GEOID_ZCTA5_20"
    )
    return dict(zip(primary["GEOID_ZCTA5_20"], primary["GEOID_COUNTY_20"], strict=False))


def _normalize_zip(value: object) -> str | None:
    match = re.search(r"\d{5}", "" if pd.isna(value) else str(value))
    return match.group(0) if match else None
