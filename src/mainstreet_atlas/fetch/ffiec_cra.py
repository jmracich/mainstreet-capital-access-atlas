"""FFIEC CRA county aggregate adapter."""

from __future__ import annotations

import logging
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pandas as pd
from requests import RequestException

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import download_file, source_record
from mainstreet_atlas.fetch.manual import prepare_manual_county_frame
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import MANUAL_DIR, PROCESSED_DIR, RAW_DIR

LOGGER = logging.getLogger(__name__)

MANUAL_PATH = MANUAL_DIR / "ffiec_cra_county.csv"
OUTPUT_PATH = PROCESSED_DIR / "ffiec_cra_county.csv"
FLAT_FILE_BASE_URL = "https://www.ffiec.gov/sites/default/files/data/cra/flat-files"


def fetch(settings: Settings, refresh: bool = False) -> dict:
    url = _aggregate_zip_url(settings.cra_year)
    try:
        zip_path = RAW_DIR / f"ffiec_cra_{settings.cra_year}_aggregate.zip"
        download_file(url, zip_path, settings, refresh=refresh)
        frame = aggregate_cra_county_originations(zip_path)
        if frame.empty:
            raise ValueError("FFIEC CRA aggregate file did not produce county-level rows")
        frame.to_csv(OUTPUT_PATH, index=False)
        status = "available"
        local_path = OUTPUT_PATH
        fetched = True
    except (RequestException, BadZipFile, OSError, ValueError) as exc:
        LOGGER.warning("Automated FFIEC CRA fetch unavailable: %s", exc)
        if MANUAL_PATH.exists():
            _prepare_manual_file()
            status = "available"
            local_path = OUTPUT_PATH
            fetched = True
        else:
            if OUTPUT_PATH.exists():
                OUTPUT_PATH.unlink()
            status = "unavailable"
            local_path = None
            fetched = False

    record = source_record(
        source_id="ffiec_cra",
        dataset_name=f"{settings.cra_year} FFIEC CRA small-business lending aggregate county file",
        publisher="Federal Financial Institutions Examination Council",
        access_method="Automated FFIEC CRA aggregate flat-file zip with manual fallback",
        url=url,
        status=status,
        coverage="County-level CRA small-business loan originations when FFIEC flat files are reachable",
        known_limitations=(
            "CRA small-business data covers reporting depository institutions and is not comprehensive "
            "of all small-business credit. FFIEC may block scripted flat-file downloads in some local "
            "environments; blocked fetches are marked unavailable rather than filled with invented data."
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
        source_label="CRA",
        required_columns={"cra_small_business_loans"},
        optional_columns=["cra_small_business_amount"],
    )
    frame.to_csv(OUTPUT_PATH, index=False)


def aggregate_cra_county_originations(zip_path: Path) -> pd.DataFrame:
    rows: dict[str, dict[str, int]] = {}
    with ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if name.endswith("/"):
                continue
            with archive.open(name) as file:
                for raw_line in file:
                    row = parse_cra_aggregate_line(raw_line.decode("latin-1", errors="ignore"))
                    if row is None:
                        continue
                    fips = str(row["fips"])
                    current = rows.setdefault(
                        fips,
                        {"cra_small_business_loans": 0, "cra_small_business_amount": 0},
                    )
                    current["cra_small_business_loans"] += int(row["cra_small_business_loans"])
                    current["cra_small_business_amount"] += int(row["cra_small_business_amount"])

    output = pd.DataFrame([{"fips": fips, **values} for fips, values in rows.items()])
    if output.empty:
        return pd.DataFrame(columns=["fips", "cra_small_business_loans", "cra_small_business_amount"])
    output["fips"] = output["fips"].astype(str).str.zfill(5)
    output["cra_small_business_loans"] = output["cra_small_business_loans"].astype(int)
    output["cra_small_business_amount"] = output["cra_small_business_amount"].astype(int)
    return output.sort_values("fips").reset_index(drop=True)


def parse_cra_aggregate_line(line: str) -> dict[str, int | str] | None:
    if len(line) < 116:
        return None
    if line[0:5].strip() != "A1-1":
        return None
    if line[10:11] != "1":
        return None
    state = line[11:13]
    county = line[13:16]
    report_level = line[33:36]
    if not state.strip() or not county.strip() or report_level != "200":
        return None

    loan_count = _fixed_int(line[36:46]) + _fixed_int(line[56:66]) + _fixed_int(line[76:86])
    loan_amount = (
        _fixed_int(line[46:56]) + _fixed_int(line[66:76]) + _fixed_int(line[86:96])
    ) * 1000
    return {
        "fips": f"{state}{county}",
        "cra_small_business_loans": loan_count,
        "cra_small_business_amount": loan_amount,
    }


def _aggregate_zip_url(year: int) -> str:
    return f"{FLAT_FILE_BASE_URL}/{str(year)[-2:]}exp_aggr.zip"


def _fixed_int(value: str) -> int:
    text = value.strip()
    return int(text) if text else 0
