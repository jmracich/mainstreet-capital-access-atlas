"""Fetch and convert Census county cartographic boundaries."""

from __future__ import annotations

import json
import logging
import zipfile
from pathlib import Path

import pandas as pd
import shapefile

from mainstreet_atlas.config import Settings
from mainstreet_atlas.constants import STATE_ABBR_TO_NAME, STATE_FIPS_TO_ABBR
from mainstreet_atlas.fetch.common import download_file, source_record
from mainstreet_atlas.generate.source_manifest import upsert_source
from mainstreet_atlas.paths import PROCESSED_DIR, RAW_DIR

LOGGER = logging.getLogger(__name__)


def county_geometry_url(year: int) -> str:
    return f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_county_500k.zip"


def _extract_zip(zip_path: Path, destination: Path) -> Path:
    marker = destination / ".extracted"
    if marker.exists():
        shp_files = list(destination.glob("*.shp"))
        if shp_files:
            return shp_files[0]

    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination)
    marker.write_text("ok", encoding="utf-8")
    shp_files = list(destination.glob("*.shp"))
    if not shp_files:
        msg = f"No shapefile found in {zip_path}"
        raise FileNotFoundError(msg)
    return shp_files[0]


def fetch(settings: Settings, refresh: bool = False) -> dict:
    url = county_geometry_url(settings.geography_year)
    zip_path = RAW_DIR / f"cb_{settings.geography_year}_us_county_500k.zip"
    extracted_dir = RAW_DIR / f"cb_{settings.geography_year}_us_county_500k"
    geojson_path = RAW_DIR / "county_geometry.geojson"
    csv_path = PROCESSED_DIR / "county_geography.csv"

    fetched = download_file(url, zip_path, settings, refresh=refresh)
    shp_path = _extract_zip(zip_path, extracted_dir)

    reader = shapefile.Reader(str(shp_path))
    field_names = [field[0] for field in reader.fields[1:]]
    features: list[dict] = []
    rows: list[dict] = []

    for shape_record in reader.iterShapeRecords():
        props = dict(zip(field_names, shape_record.record, strict=False))
        state_fips = str(props.get("STATEFP", "")).zfill(2)
        county_fips = str(props.get("COUNTYFP", "")).zfill(3)
        fips = str(props.get("GEOID") or f"{state_fips}{county_fips}").zfill(5)
        state_abbr = STATE_FIPS_TO_ABBR.get(state_fips, state_fips)
        county_name = str(props.get("NAME") or props.get("NAMELSAD") or "").strip()
        state_name = STATE_ABBR_TO_NAME.get(state_abbr, state_abbr)
        lat = _safe_float(props.get("INTPTLAT"))
        lon = _safe_float(props.get("INTPTLON"))
        public_props = {
            "fips": fips,
            "county_name": county_name,
            "state_fips": state_fips,
            "state_abbr": state_abbr,
            "state_name": state_name,
            "namelsad": str(props.get("NAMELSAD") or f"{county_name} County"),
            "lat": lat,
            "lon": lon,
        }
        features.append(
            {
                "type": "Feature",
                "properties": public_props,
                "geometry": shape_record.shape.__geo_interface__,
            }
        )
        rows.append(public_props)

    geojson_path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")),
        encoding="utf-8",
    )
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    LOGGER.info("Wrote %s county geography rows", len(rows))

    record = source_record(
        source_id="census_county_geometry",
        dataset_name=f"{settings.geography_year} Census Cartographic Boundary File, Counties",
        publisher="U.S. Census Bureau",
        access_method="Automated download of official cartographic boundary shapefile",
        url=url,
        status="available",
        coverage="U.S. counties and county equivalents represented in Census cartographic files",
        known_limitations="Geometry is simplified for thematic mapping and is not a legal boundary product.",
        local_path=geojson_path,
        fetched=fetched or geojson_path.exists(),
    )
    upsert_source(record)
    return record


def _safe_float(value: object) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None
