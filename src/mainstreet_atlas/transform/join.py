"""Join source datasets and create public county indicators."""

from __future__ import annotations

import json
import logging

import pandas as pd

from mainstreet_atlas.generate.data_dictionary import write_data_dictionary
from mainstreet_atlas.generate.data_package import write_data_package_manifest
from mainstreet_atlas.paths import PROCESSED_DIR, PUBLIC_DATA_DIR, RAW_DIR
from mainstreet_atlas.schemas import validate_public_county_export
from mainstreet_atlas.transform.clean import ensure_fips, numeric_columns
from mainstreet_atlas.transform.scoring import score_counties

LOGGER = logging.getLogger(__name__)

MAP_EXCLUDED_STATE_ABBRS = {"AK", "HI", "AS", "GU", "MP", "PR", "VI"}
MAP_BASE_PROPERTY_COLUMNS = ["fips", "county_name", "state_abbr"]
MAP_INDICATOR_PROPERTY_COLUMNS = [
    "support_priority_signal",
    "data_quality_grade",
    "establishments",
    "branch_count",
    "branches_per_10k_residents",
    "branches_per_1000_establishments",
    "cra_small_business_loans",
    "cra_loans_per_1000_establishments",
    "poverty_pct",
    "median_household_income",
    "housing_cost_pressure",
]


def build_county_dataset() -> pd.DataFrame:
    geography = _load_required(PROCESSED_DIR / "county_geography.csv")
    geography["fips"] = ensure_fips(geography["fips"])
    frame = geography.copy()

    for file_name in [
        "cbp_county.csv",
        "population_estimates_county.csv",
        "saipe_county.csv",
        "acs_county.csv",
        "fdic_branches_county.csv",
        "fdic_sod_county.csv",
        "bls_laus_county.csv",
        "ffiec_cra_county.csv",
        "sba_county.csv",
        "cdfi_county.csv",
        "hud_county.csv",
    ]:
        path = PROCESSED_DIR / file_name
        if not path.exists():
            LOGGER.info("Optional processed file is absent: %s", path)
            continue
        right = pd.read_csv(path, dtype={"fips": str})
        right["fips"] = ensure_fips(right["fips"])
        frame = frame.merge(right, on="fips", how="left")

    frame = _ensure_public_schema(frame)
    if "acs_population" in frame.columns:
        frame["population"] = frame["population"].combine_first(frame["acs_population"])
    if "saipe_poverty_pct" in frame.columns:
        frame["poverty_pct"] = frame["poverty_pct"].combine_first(frame["saipe_poverty_pct"])
    if "saipe_median_household_income" in frame.columns:
        frame["median_household_income"] = frame["median_household_income"].combine_first(
            frame["saipe_median_household_income"]
        )
    frame = numeric_columns(
        frame,
        [
            "acs_population",
            "households",
            "population",
            "population_estimate_year",
            "population_estimates_base_2020",
            "saipe_poverty_count",
            "saipe_poverty_pct",
            "saipe_median_household_income",
            "income_poverty_estimate_year",
            "median_household_income",
            "poverty_pct",
            "unemployment_pct",
            "labor_force",
            "employed",
            "unemployed",
            "unemployment_year",
            "rent_burden_pct",
            "no_vehicle_pct",
            "no_internet_pct",
            "education_population_25_plus",
            "bachelors_or_higher_population",
            "bachelors_or_higher_pct",
            "establishments",
            "business_employment",
            "annual_payroll_thousands",
            "small_establishments_under_20",
            "small_establishments_under_20_pct",
            "top_industry_establishments",
            "top_industry_establishment_share",
            "branch_count",
            "sod_year",
            "sod_branch_records",
            "branch_deposits_thousands",
            "cra_small_business_loans",
            "sba_loan_count",
            "cdfi_count",
            "fmr_to_income_pct",
            "two_bedroom_fmr",
        ],
    )
    scored = score_counties(frame)
    scored = scored.sort_values(["support_priority_signal", "state_abbr", "county_name"], ascending=[False, True, True])
    validate_public_county_export(scored)

    output_path = PROCESSED_DIR / "county_indicators.csv"
    public_csv_path = PUBLIC_DATA_DIR / "counties.csv"
    public_json_path = PUBLIC_DATA_DIR / "counties.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_path, index=False)
    scored.to_csv(public_csv_path, index=False)
    public_json_path.write_text(scored.to_json(orient="records", indent=2), encoding="utf-8")
    write_data_dictionary(list(scored.columns))

    _write_public_geojson(scored)
    write_data_package_manifest()
    LOGGER.info("Wrote %s scored county rows", len(scored))
    return scored


def _ensure_public_schema(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    expected_columns = [
        "population",
        "acs_population",
        "households",
        "population_estimate_year",
        "population_estimates_base_2020",
        "saipe_poverty_count",
        "saipe_poverty_pct",
        "saipe_median_household_income",
        "income_poverty_estimate_year",
        "median_household_income",
        "poverty_pct",
        "unemployment_pct",
        "labor_force",
        "employed",
        "unemployed",
        "unemployment_year",
        "rent_burden_pct",
        "no_vehicle_pct",
        "no_internet_pct",
        "education_population_25_plus",
        "bachelors_or_higher_population",
        "bachelors_or_higher_pct",
        "establishments",
        "business_employment",
        "annual_payroll_thousands",
        "small_establishments_under_20",
        "small_establishments_under_20_pct",
        "top_industry_naics2",
        "top_industry_name",
        "top_industry_establishments",
        "top_industry_establishment_share",
        "branch_count",
        "sod_year",
        "sod_branch_records",
        "branch_deposits_thousands",
        "cra_small_business_loans",
        "cra_small_business_amount",
        "sba_loan_count",
        "sba_loan_amount",
        "cdfi_count",
        "fmr_to_income_pct",
        "two_bedroom_fmr",
    ]
    for column in expected_columns:
        if column not in output.columns:
            output[column] = pd.NA
    return output


def _load_required(path):
    if not path.exists():
        msg = f"Required processed file not found: {path}. Run `make fetch` first."
        raise FileNotFoundError(msg)
    return pd.read_csv(path, dtype={"fips": str})


def _write_public_geojson(scored: pd.DataFrame) -> None:
    source_geojson = RAW_DIR / "county_geometry.geojson"
    destination = PUBLIC_DATA_DIR / "county-map.geojson"
    if not source_geojson.exists():
        LOGGER.warning("No county geometry GeoJSON found; map asset will be absent")
        return

    property_frame = scored.set_index("fips").reindex(columns=MAP_INDICATOR_PROPERTY_COLUMNS)
    properties = property_frame.to_dict(orient="index")

    payload = json.loads(source_geojson.read_text(encoding="utf-8"))
    map_features = []
    for feature in payload.get("features", []):
        source_props = feature.get("properties", {})
        if source_props.get("state_abbr") in MAP_EXCLUDED_STATE_ABBRS:
            continue

        fips = str(source_props.get("fips", "")).zfill(5)
        map_props = {key: source_props.get(key) for key in MAP_BASE_PROPERTY_COLUMNS}
        for key, value in properties.get(fips, {}).items():
            if pd.isna(value):
                map_props[key] = None
            else:
                map_props[key] = value
        map_features.append(
            {
                "type": "Feature",
                "properties": map_props,
                "geometry": feature.get("geometry"),
            }
        )
    payload["features"] = map_features
    destination.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    legacy_path = PUBLIC_DATA_DIR / "counties.geojson"
    if legacy_path.exists():
        legacy_path.unlink()
