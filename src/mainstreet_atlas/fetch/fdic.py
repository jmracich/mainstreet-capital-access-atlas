"""Fetch FDIC BankFind branch and Summary of Deposits context."""

from __future__ import annotations

import logging

import pandas as pd
from requests import RequestException

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import normalize_county_name, request_session, source_record
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import PROCESSED_DIR

LOGGER = logging.getLogger(__name__)

FDIC_LOCATIONS_URL = "https://banks.data.fdic.gov/api/locations"
FDIC_SOD_URL = "https://banks.data.fdic.gov/api/sod"


def fetch(settings: Settings, refresh: bool = False) -> dict:
    branch_record = _fetch_branch_locations(settings, refresh=refresh)
    _fetch_summary_of_deposits(settings, refresh=refresh)
    return branch_record


def _fetch_branch_locations(settings: Settings, refresh: bool = False) -> dict:
    output_path = PROCESSED_DIR / "fdic_branches_county.csv"
    if output_path.exists() and not refresh:
        status = "available"
        fetched = True
    else:
        geography_path = PROCESSED_DIR / "county_geography.csv"
        if not geography_path.exists():
            status = "unavailable"
            fetched = False
            LOGGER.warning("Skipping FDIC aggregation because county geography is not built")
        else:
            frame = _fetch_locations(settings)
            county = _aggregate_to_fips(frame, pd.read_csv(geography_path, dtype={"fips": str}))
            county.to_csv(output_path, index=False)
            status = "available"
            fetched = True
            LOGGER.info("Wrote %s FDIC county branch rows", len(county))

    record = source_record(
        source_id="fdic_bankfind",
        dataset_name="FDIC BankFind Suite branch locations",
        publisher="Federal Deposit Insurance Corporation",
        access_method="FDIC BankFind public API",
        url=FDIC_LOCATIONS_URL,
        status=status,
        coverage="Open FDIC BankFind branch location records aggregated to county where matched",
        known_limitations=(
            "County matching uses branch county and state names against Census county names. Branch "
            "presence is not a full measure of local capital access."
        ),
        local_path=output_path if output_path.exists() else None,
        fetched=fetched,
    )
    upsert_source(record)
    return record


def _fetch_summary_of_deposits(settings: Settings, refresh: bool = False) -> dict:
    output_path = PROCESSED_DIR / "fdic_sod_county.csv"
    fetched = False
    if output_path.exists() and not refresh:
        status = "available"
    else:
        try:
            frame = _fetch_latest_sod(settings)
        except RequestException as exc:
            status = "unavailable"
            LOGGER.warning("Skipping FDIC Summary of Deposits because the API request failed: %s", exc)
        else:
            frame.to_csv(output_path, index=False)
            status = "available"
            fetched = True
            LOGGER.info("Wrote %s FDIC SOD county rows", len(frame))

    record = source_record(
        source_id="fdic_sod",
        dataset_name="FDIC Summary of Deposits",
        publisher="Federal Deposit Insurance Corporation",
        access_method="FDIC BankFind Summary of Deposits public API",
        url=FDIC_SOD_URL,
        status=status,
        coverage="County-level branch deposit survey records aggregated from the latest available SOD year",
        known_limitations=(
            "Deposits are reported by branch office and are not a direct measure of small-business "
            "lending, credit access, or local reinvestment."
        ),
        local_path=output_path if output_path.exists() else None,
        fetched=fetched,
    )
    upsert_source(record)
    return record


def _fetch_locations(settings: Settings) -> pd.DataFrame:
    session = request_session(settings)
    records: list[dict] = []
    limit = 10000
    offset = 0

    while True:
        params = {
            "fields": "STALP,COUNTY,CITY,ADDRESS,ZIP,LATITUDE,LONGITUDE",
            "limit": limit,
            "offset": offset,
            "format": "json",
        }
        response = session.get(FDIC_LOCATIONS_URL, params=params, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        page = [item.get("data", {}) for item in payload.get("data", [])]
        records.extend(page)
        LOGGER.info("Fetched %s FDIC branch records", len(records))
        if len(page) < limit:
            break
        offset += limit

    return pd.DataFrame(records)


def _fetch_latest_sod(settings: Settings) -> pd.DataFrame:
    session = request_session(settings)
    latest_response = session.get(
        FDIC_SOD_URL,
        params={
            "fields": "YEAR",
            "sort_by": "YEAR",
            "sort_order": "desc",
            "limit": 1,
            "format": "json",
        },
        timeout=settings.request_timeout_seconds,
    )
    latest_response.raise_for_status()
    latest_payload = latest_response.json()
    latest_year = latest_payload["data"][0]["data"]["YEAR"]

    records: list[dict] = []
    limit = 10000
    offset = 0
    while True:
        response = session.get(
            FDIC_SOD_URL,
            params={
                "filters": f"YEAR:{latest_year}",
                "fields": "YEAR,STCNTY,DEPSUMBR",
                "limit": limit,
                "offset": offset,
                "format": "json",
            },
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        page = [item.get("data", {}) for item in payload.get("data", [])]
        records.extend(page)
        LOGGER.info("Fetched %s FDIC SOD records for %s", len(records), latest_year)
        if len(page) < limit:
            break
        offset += limit

    return _aggregate_sod_to_fips(pd.DataFrame(records))


def _aggregate_to_fips(locations: pd.DataFrame, geography: pd.DataFrame) -> pd.DataFrame:
    if locations.empty:
        return pd.DataFrame(columns=["fips", "branch_count"])

    lookup = geography.copy()
    lookup["county_key"] = lookup["county_name"].map(normalize_county_name)
    lookup["state_abbr"] = lookup["state_abbr"].astype(str).str.upper()
    lookup = lookup[["fips", "state_abbr", "county_key"]].drop_duplicates()

    locations = locations.copy()
    locations["state_abbr"] = locations["STALP"].astype(str).str.upper()
    locations["county_key"] = locations["COUNTY"].map(normalize_county_name)
    merged = locations.merge(lookup, on=["state_abbr", "county_key"], how="left")
    matched = merged.dropna(subset=["fips"])
    return (
        matched.groupby("fips", as_index=False)
        .size()
        .rename(columns={"size": "branch_count"})
        .astype({"fips": str})
    )


def _aggregate_sod_to_fips(sod: pd.DataFrame) -> pd.DataFrame:
    if sod.empty:
        return pd.DataFrame(
            columns=["fips", "sod_year", "sod_branch_records", "branch_deposits_thousands"]
        )

    frame = sod.copy()
    frame["fips"] = frame["STCNTY"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    frame["sod_year"] = pd.to_numeric(frame["YEAR"], errors="coerce")
    frame["branch_deposits_thousands"] = pd.to_numeric(frame["DEPSUMBR"], errors="coerce")
    grouped = (
        frame.groupby("fips", as_index=False)
        .agg(
            sod_year=("sod_year", "max"),
            sod_branch_records=("branch_deposits_thousands", "size"),
            branch_deposits_thousands=("branch_deposits_thousands", "sum"),
        )
        .astype({"fips": str})
    )
    return grouped
