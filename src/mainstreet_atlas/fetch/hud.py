"""Optional HUD housing-cost context adapter."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from requests import RequestException

from mainstreet_atlas.config import Settings
from mainstreet_atlas.fetch.common import request_session, source_record
from mainstreet_atlas.fetch.manual import prepare_manual_county_frame
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import MANUAL_DIR, PROCESSED_DIR

LOGGER = logging.getLogger(__name__)

MANUAL_PATH = MANUAL_DIR / "hud_county.csv"
OUTPUT_PATH = PROCESSED_DIR / "hud_county.csv"
HUD_FMR_URL = "https://www.huduser.gov/portal/dataset/fmr-api.html"
HUD_FMR_API_BASE = "https://www.huduser.gov/hudapi/public/fmr"


def fetch(settings: Settings, refresh: bool = False) -> dict:
    if OUTPUT_PATH.exists() and not refresh:
        status = "available"
        local_path = OUTPUT_PATH
        fetched = True
    elif settings.hud_api_token:
        try:
            frame = fetch_hud_fmr_counties(settings)
            if frame.empty:
                raise ValueError("HUD API did not return county FMR rows")
            frame.to_csv(OUTPUT_PATH, index=False)
            status = "available"
            local_path = OUTPUT_PATH
            fetched = True
        except (RequestException, ValueError) as exc:
            LOGGER.warning("Automated HUD fetch unavailable: %s", exc)
            status, local_path, fetched = _manual_fallback()
    else:
        status, local_path, fetched = _manual_fallback(default_status="optional_token")

    record = source_record(
        source_id="hud_fmr",
        dataset_name="HUD Fair Market Rents / Income Limits county context",
        publisher="U.S. Department of Housing and Urban Development",
        access_method="HUD Fair Market Rents API with optional HUD_API_TOKEN",
        url=HUD_FMR_URL,
        status=status,
        coverage="County-level housing pressure context when configured or supplied",
        known_limitations=(
            "HUD API access requires a HUD User token. FMR-to-income context uses the latest available "
            "HUD two-bedroom FMR and Census SAIPE median household income when both are present."
        ),
        local_path=local_path,
        fetched=fetched,
    )
    upsert_source(record)
    return record


def fetch_hud_fmr_counties(settings: Settings) -> pd.DataFrame:
    session = request_session(settings)
    session.headers.update({"Authorization": f"Bearer {settings.hud_api_token}"})
    rows = []
    for state_abbr in _state_abbrs():
        response = session.get(
            f"{HUD_FMR_API_BASE}/statedata/{state_abbr}",
            timeout=settings.request_timeout_seconds,
        )
        if response.status_code == 404:
            LOGGER.info("No HUD FMR state data returned for %s", state_abbr)
            continue
        response.raise_for_status()
        rows.extend(parse_hud_state_payload(response.json()))

    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=["fips", "two_bedroom_fmr", "fmr_to_income_pct"])
    frame = frame.dropna(subset=["fips", "two_bedroom_fmr"]).drop_duplicates("fips")
    income_lookup = _median_income_lookup()
    frame["median_household_income"] = frame["fips"].map(income_lookup)
    frame["fmr_to_income_pct"] = (
        frame["two_bedroom_fmr"] * 12 / frame["median_household_income"]
    ) * 100
    return frame[["fips", "two_bedroom_fmr", "fmr_to_income_pct"]].sort_values("fips")


def parse_hud_state_payload(payload: dict) -> list[dict[str, float | str]]:
    data = payload.get("data", payload)
    counties = data.get("counties", []) if isinstance(data, dict) else []
    rows = []
    for county in counties:
        fips = _hud_fips(county.get("code") or county.get("fips_code"))
        two_bedroom_fmr = _number(county.get("Two-Bedroom") or county.get("two_bedroom"))
        if fips and two_bedroom_fmr is not None:
            rows.append({"fips": fips, "two_bedroom_fmr": two_bedroom_fmr})
    return rows


def _manual_fallback(default_status: str = "unavailable") -> tuple[str, Path | None, bool]:
    if MANUAL_PATH.exists():
        frame = pd.read_csv(MANUAL_PATH, dtype={"fips": str})
        frame = prepare_manual_county_frame(
            frame,
            source_label="HUD",
            required_columns=set(),
            optional_columns=["two_bedroom_fmr", "fmr_to_income_pct"],
        )
        frame.to_csv(OUTPUT_PATH, index=False)
        return "available", OUTPUT_PATH, True

    LOGGER.info("No manual HUD file found at %s", MANUAL_PATH)
    return default_status, None, False


def _state_abbrs() -> list[str]:
    geography_path = PROCESSED_DIR / "county_geography.csv"
    if not geography_path.exists():
        return []
    geography = pd.read_csv(geography_path, dtype={"fips": str})
    return sorted(geography["state_abbr"].dropna().astype(str).unique())


def _median_income_lookup() -> dict[str, float]:
    path = PROCESSED_DIR / "saipe_county.csv"
    if not path.exists():
        return {}
    frame = pd.read_csv(path, dtype={"fips": str})
    income = pd.to_numeric(frame.get("saipe_median_household_income"), errors="coerce")
    return dict(zip(frame["fips"].astype(str).str.zfill(5), income, strict=False))


def _hud_fips(value: object) -> str | None:
    text = "" if value is None else str(value).strip()
    if not text[:1].isdigit():
        return None
    digits = "".join(char for char in text if char.isdigit())
    if len(digits) < 5:
        return None
    return digits[:5]


def _number(value: object) -> float | None:
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else float(number)
