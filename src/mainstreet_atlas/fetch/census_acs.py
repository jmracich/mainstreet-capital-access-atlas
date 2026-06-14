"""Optional Census ACS 5-year API adapter."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from mainstreet_atlas.config import Settings
from mainstreet_atlas.constants import STATE_FIPS_TO_ABBR
from mainstreet_atlas.fetch.common import request_session, source_record
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import PROCESSED_DIR

LOGGER = logging.getLogger(__name__)

ACS_VARIABLES = {
    "B01003_001E": "acs_population",
    "B11001_001E": "households",
    "B19013_001E": "median_household_income",
    "B17001_001E": "poverty_universe",
    "B17001_002E": "population_in_poverty",
    "B23025_003E": "labor_force",
    "B23025_005E": "unemployed",
    "B25070_001E": "rent_burden_universe",
    "B25070_007E": "rent_30_34",
    "B25070_008E": "rent_35_39",
    "B25070_009E": "rent_40_49",
    "B25070_010E": "rent_50_plus",
    "B08201_001E": "vehicle_households",
    "B08201_002E": "no_vehicle_households",
    "B28002_001E": "internet_households",
    "B28002_013E": "no_internet_households",
    "B15003_001E": "education_population_25_plus",
    "B15003_022E": "bachelors_degree",
    "B15003_023E": "masters_degree",
    "B15003_024E": "professional_degree",
    "B15003_025E": "doctorate_degree",
}


def fetch(settings: Settings, refresh: bool = False) -> dict:
    output_path = PROCESSED_DIR / "acs_county.csv"
    url = f"https://api.census.gov/data/{settings.acs_year}/acs/acs5"
    if output_path.exists() and not refresh:
        status = "available"
        fetched = True
    elif not settings.census_api_key:
        status = "optional_token"
        fetched = False
        LOGGER.info("Skipping ACS fetch because CENSUS_API_KEY is not set")
    else:
        frame = _fetch_api(settings, url)
        frame.to_csv(output_path, index=False)
        status = "available"
        fetched = True
        LOGGER.info("Wrote %s ACS county rows", len(frame))

    record = source_record(
        source_id="census_acs",
        dataset_name=f"{settings.acs_year} ACS 5-year detailed tables",
        publisher="U.S. Census Bureau",
        access_method="Census API; optional CENSUS_API_KEY environment variable",
        url=url,
        status=status,
        coverage="County-level ACS indicators when API access is configured",
        known_limitations=(
            "ACS is survey-based, lagged, and includes margins of error. The default build marks "
            "this source unavailable when no Census API key is present."
        ),
        local_path=output_path if output_path.exists() else None,
        fetched=fetched,
    )
    upsert_source(record)
    return record


def _fetch_api(settings: Settings, url: str) -> pd.DataFrame:
    session = request_session(settings)
    rows: list[dict[str, Any]] = []
    variables = ["NAME", *ACS_VARIABLES]

    _verify_variables(session, settings, variables[1:])

    for state_fips in STATE_FIPS_TO_ABBR:
        params = {
            "get": ",".join(variables),
            "for": "county:*",
            "in": f"state:{state_fips}",
            "key": settings.census_api_key,
        }
        response = session.get(url, params=params, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        if response.status_code == 204 or not response.text.strip():
            LOGGER.info("No ACS county rows returned for state FIPS %s", state_fips)
            continue
        payload = response.json()
        if len(payload) <= 1:
            continue
        header = payload[0]
        rows.extend(dict(zip(header, row, strict=False)) for row in payload[1:])

    return _transform_acs_rows(rows)


def _transform_acs_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["fips"] = frame["state"].astype(str).str.zfill(2) + frame["county"].astype(str).str.zfill(3)
    for source, target in ACS_VARIABLES.items():
        frame[target] = pd.to_numeric(frame[source], errors="coerce")
    output = frame[["fips", *ACS_VARIABLES.values()]].copy()
    output["poverty_pct"] = _ratio(output["population_in_poverty"], output["poverty_universe"]) * 100
    output["unemployment_pct"] = _ratio(output["unemployed"], output["labor_force"]) * 100
    rent_burdened = (
        output["rent_30_34"]
        + output["rent_35_39"]
        + output["rent_40_49"]
        + output["rent_50_plus"]
    )
    output["rent_burden_pct"] = _ratio(rent_burdened, output["rent_burden_universe"]) * 100
    output["no_vehicle_pct"] = (
        _ratio(output["no_vehicle_households"], output["vehicle_households"]) * 100
    )
    output["no_internet_pct"] = (
        _ratio(output["no_internet_households"], output["internet_households"]) * 100
    )
    output["bachelors_or_higher_population"] = (
        output["bachelors_degree"]
        + output["masters_degree"]
        + output["professional_degree"]
        + output["doctorate_degree"]
    )
    output["bachelors_or_higher_pct"] = (
        _ratio(output["bachelors_or_higher_population"], output["education_population_25_plus"])
        * 100
    )
    return output[
        [
            "fips",
            "acs_population",
            "households",
            "median_household_income",
            "poverty_pct",
            "labor_force",
            "unemployed",
            "unemployment_pct",
            "rent_burden_pct",
            "no_vehicle_pct",
            "no_internet_pct",
            "education_population_25_plus",
            "bachelors_or_higher_population",
            "bachelors_or_higher_pct",
        ]
    ]


def _verify_variables(session, settings: Settings, variable_names: list[str]) -> None:
    url = f"https://api.census.gov/data/{settings.acs_year}/acs/acs5/variables.json"
    response = session.get(url, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    available = set(response.json()["variables"])
    missing = sorted(set(variable_names) - available)
    if missing:
        msg = f"ACS variables missing from metadata: {', '.join(missing)}"
        raise ValueError(msg)


def _ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.where(denominator != 0)
    return numerator / denominator
