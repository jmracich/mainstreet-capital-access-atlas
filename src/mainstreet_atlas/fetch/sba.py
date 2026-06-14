"""Automated SBA county lending adapter."""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
from requests import RequestException

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import (
    download_file,
    normalize_county_name,
    request_session,
    source_record,
)
from mainstreet_atlas.fetch.manual import prepare_manual_county_frame
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import MANUAL_DIR, PROCESSED_DIR, RAW_DIR

LOGGER = logging.getLogger(__name__)

MANUAL_PATH = MANUAL_DIR / "sba_county.csv"
OUTPUT_PATH = PROCESSED_DIR / "sba_county.csv"
PACKAGE_URL = "https://data.sba.gov/api/3/action/package_show?id=7-a-504-foia"
RESOURCE_PATTERNS = [
    re.compile(r"FOIA\s*-\s*7\(a\).*FY2020-Present", re.IGNORECASE),
    re.compile(r"FOIA\s*-\s*504.*FY2010-Present", re.IGNORECASE),
]


def fetch(settings: Settings, refresh: bool = False) -> dict:
    try:
        resources = _current_resource_urls(settings)
        raw_paths = [_download_resource(resource, settings, refresh=refresh) for resource in resources]
        frame = aggregate_sba_county_lending(raw_paths)
        if frame.empty:
            raise ValueError("SBA automated sources did not produce county-level rows")
        frame.to_csv(OUTPUT_PATH, index=False)
        status = "available"
        local_path = OUTPUT_PATH
        fetched = True
    except (RequestException, ValueError, OSError, pd.errors.ParserError) as exc:
        LOGGER.warning("Automated SBA fetch unavailable: %s", exc)
        if not MANUAL_PATH.exists():
            status = "unavailable"
            local_path = None
            fetched = False
        else:
            LOGGER.info("Falling back to manual SBA file at %s", MANUAL_PATH)
            _prepare_manual_file()
            status = "available"
            local_path = OUTPUT_PATH
            fetched = True

    record = source_record(
        source_id="sba",
        dataset_name="SBA 7(a)/504 lending county aggregate",
        publisher="U.S. Small Business Administration",
        access_method="Automated SBA Open Data CKAN API with strict county aggregation",
        url=PACKAGE_URL,
        status=status,
        coverage="County-level SBA lending activity from latest available public FOIA current-period files",
        known_limitations=(
            "SBA FOIA source files include row-level public borrower records in ignored raw cache files; "
            "only county aggregates are published. County matching uses SBA project county and state names."
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
        source_label="SBA",
        required_columns={"sba_loan_count"},
        optional_columns=["sba_loan_amount"],
    )
    frame.to_csv(OUTPUT_PATH, index=False)


def _current_resource_urls(settings: Settings) -> list[dict]:
    session = request_session(settings)
    response = session.get(PACKAGE_URL, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise ValueError("SBA package_show response was not successful")

    resources = []
    for resource in payload.get("result", {}).get("resources", []):
        name = str(resource.get("name") or "")
        fmt = str(resource.get("format") or "").upper()
        url = str(resource.get("url") or "")
        if fmt == "CSV" and url and any(pattern.search(name) for pattern in RESOURCE_PATTERNS):
            resources.append(resource)

    if len(resources) < len(RESOURCE_PATTERNS):
        raise ValueError("SBA current 7(a) and 504 CSV resources were not both found")
    return resources


def _download_resource(resource: dict, settings: Settings, *, refresh: bool) -> Path:
    resource_id = str(resource.get("id") or _slug(resource.get("name", "sba_resource")))
    destination = RAW_DIR / f"sba_{resource_id}.csv"
    download_file(str(resource["url"]), destination, settings, refresh=refresh)
    return destination


def aggregate_sba_county_lending(paths: list[Path], *, chunksize: int = 100_000) -> pd.DataFrame:
    lookup = _county_lookup()
    aggregates: dict[tuple[int, str], dict[str, float]] = defaultdict(
        lambda: {"sba_loan_count": 0, "sba_loan_amount": 0.0}
    )
    latest_year: int | None = None

    for path in paths:
        for chunk in pd.read_csv(
            path,
            usecols=["projectcounty", "projectstate", "approvalfy", "grossapproval"],
            chunksize=chunksize,
            dtype=str,
            encoding_errors="replace",
            low_memory=False,
        ):
            prepared = _prepare_sba_chunk(chunk, lookup)
            if prepared.empty:
                continue
            latest_year = int(prepared["approvalfy"].max()) if latest_year is None else max(
                latest_year, int(prepared["approvalfy"].max())
            )
            grouped = prepared.groupby(["approvalfy", "fips"], as_index=False).agg(
                sba_loan_count=("grossapproval", "size"),
                sba_loan_amount=("grossapproval", "sum"),
            )
            for row in grouped.itertuples(index=False):
                key = (int(row.approvalfy), str(row.fips))
                aggregates[key]["sba_loan_count"] += int(row.sba_loan_count)
                aggregates[key]["sba_loan_amount"] += float(row.sba_loan_amount)

    if latest_year is None:
        return pd.DataFrame(columns=["fips", "sba_loan_count", "sba_loan_amount"])

    rows = [
        {"fips": fips, **values}
        for (year, fips), values in aggregates.items()
        if year == latest_year
    ]
    output = pd.DataFrame(rows)
    if output.empty:
        return output
    output["sba_loan_count"] = output["sba_loan_count"].astype(int)
    output["sba_loan_amount"] = output["sba_loan_amount"].round(0)
    return output.sort_values("fips").reset_index(drop=True)


def _prepare_sba_chunk(chunk: pd.DataFrame, lookup: dict[tuple[str, str], str]) -> pd.DataFrame:
    output = chunk.copy()
    output["approvalfy"] = pd.to_numeric(output["approvalfy"], errors="coerce")
    output["grossapproval"] = pd.to_numeric(output["grossapproval"], errors="coerce").fillna(0)
    output["state"] = output["projectstate"].astype(str).str.strip().str.upper()
    output["county_key"] = output["projectcounty"].map(_county_key)
    output["fips"] = [
        lookup.get((state, county))
        for state, county in zip(output["state"], output["county_key"], strict=False)
    ]
    return output.dropna(subset=["approvalfy", "fips"])


def _county_lookup() -> dict[tuple[str, str], str]:
    geography_path = PROCESSED_DIR / "county_geography.csv"
    if not geography_path.exists():
        raise ValueError("County geography must be fetched before SBA county aggregation")

    geography = pd.read_csv(geography_path, dtype={"fips": str})
    lookup: dict[tuple[str, str], str] = {}
    for row in geography.itertuples(index=False):
        lookup[(row.state_abbr, _county_key(row.county_name))] = str(row.fips).zfill(5)
    return lookup


def _county_key(value: object) -> str:
    text = normalize_county_name(value)
    text = text.replace("SAINT ", "ST ")
    text = text.replace("STE ", "ST ")
    text = text.replace("DE KALB", "DEKALB")
    return text


def _slug(value: object) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", str(value)).strip("_").lower()
    return text or "resource"
