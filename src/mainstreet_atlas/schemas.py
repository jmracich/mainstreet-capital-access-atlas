"""Lightweight schemas for generated public metadata."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from mainstreet_atlas.constants import STATE_ABBR_TO_FIPS

PUBLIC_EXPORT_REQUIRED_COLUMNS = [
    "fips",
    "county_name",
    "state_fips",
    "state_abbr",
    "state_name",
    "support_priority_signal",
    "data_completeness",
    "data_quality_gap",
    "data_quality_grade",
    "score_component_coverage",
    "substantive_component_coverage",
    "missing_source_fields",
]

SCORE_COMPONENT_COLUMNS = [
    "small_business_importance",
    "capital_access_visibility_gap",
    "community_economic_stress",
    "housing_cost_pressure",
    "local_support_ecosystem_gap",
    "data_quality_gap",
    "support_priority_signal",
]

FRACTION_COLUMNS = [
    "data_completeness",
    "score_component_coverage",
    "substantive_component_coverage",
]


class SourceRecord(BaseModel):
    id: str
    dataset_name: str
    publisher: str
    access_method: str
    url: str | None = None
    status: Literal["available", "unavailable", "manual_optional", "optional_token"]
    last_fetched: str | None = None
    coverage: str
    known_limitations: str
    local_path: str | None = None

    @field_validator("last_fetched")
    @classmethod
    def validate_timestamp(cls, value: str | None) -> str | None:
        if value:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class CountyRecord(BaseModel):
    model_config = ConfigDict(extra="allow", allow_inf_nan=False)

    fips: str = Field(min_length=5, max_length=5)
    county_name: str
    state_fips: str | None = Field(default=None, min_length=2, max_length=2)
    state_abbr: str = Field(min_length=2, max_length=2)
    support_priority_signal: float | None = Field(default=None, ge=0, le=100)
    data_completeness: float = Field(default=0.0, ge=0, le=1)
    score_component_coverage: float = Field(default=0.0, ge=0, le=1)
    substantive_component_coverage: float = Field(default=0.0, ge=0, le=1)
    data_quality_grade: Literal["A", "B", "C", "D"]

    @field_validator("fips")
    @classmethod
    def validate_fips(cls, value: str) -> str:
        if not value.isdigit():
            msg = "FIPS must contain only digits"
            raise ValueError(msg)
        return value

    @field_validator("state_fips")
    @classmethod
    def validate_state_fips(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.isdigit():
            msg = "State FIPS must contain only digits"
            raise ValueError(msg)
        return value

    @field_validator("state_abbr")
    @classmethod
    def validate_state_abbr(cls, value: str) -> str:
        if value not in STATE_ABBR_TO_FIPS:
            msg = f"Unsupported state abbreviation: {value}"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_score_availability(self) -> CountyRecord:
        if self.state_fips and self.fips[:2] != self.state_fips:
            msg = f"County FIPS {self.fips} does not match state FIPS {self.state_fips}"
            raise ValueError(msg)
        if self.support_priority_signal is None and self.substantive_component_coverage > 0:
            msg = "Support Priority Signal is missing despite available substantive components"
            raise ValueError(msg)
        if self.score_component_coverage < self.substantive_component_coverage:
            msg = "Score component coverage cannot be lower than substantive component coverage"
            raise ValueError(msg)
        return self


def validate_public_county_export(frame: pd.DataFrame) -> None:
    """Validate the generated county export before it is written publicly."""

    errors: list[str] = []
    missing_columns = [column for column in PUBLIC_EXPORT_REQUIRED_COLUMNS if column not in frame]
    if missing_columns:
        errors.append(f"Missing required public columns: {', '.join(missing_columns)}")
        raise ValueError("; ".join(errors))

    if frame.empty:
        errors.append("Public county export is empty")

    fips = frame["fips"].map(_normalize_code)
    invalid_fips = fips.isna() | ~fips.str.fullmatch(r"\d{5}", na=False)
    if invalid_fips.any():
        errors.append(_sample_error("Invalid county FIPS values", frame.loc[invalid_fips, "fips"]))

    duplicate_fips = fips[fips.duplicated(keep=False)]
    if not duplicate_fips.empty:
        errors.append(_sample_error("Duplicate county FIPS values", duplicate_fips))

    state_fips = frame["state_fips"].map(lambda value: _normalize_code(value, width=2))
    invalid_state_fips = state_fips.isna() | ~state_fips.str.fullmatch(r"\d{2}", na=False)
    if invalid_state_fips.any():
        errors.append(
            _sample_error("Invalid state FIPS values", frame.loc[invalid_state_fips, "state_fips"])
        )

    mismatched_state = fips.str[:2].ne(state_fips) & fips.notna() & state_fips.notna()
    if mismatched_state.any():
        errors.append(_sample_error("County FIPS/state FIPS mismatches", frame.loc[mismatched_state, "fips"]))

    blank_counties = frame["county_name"].astype(str).str.strip().eq("")
    if blank_counties.any():
        errors.append(_sample_error("Blank county names", frame.loc[blank_counties, "fips"]))

    state_abbr = frame["state_abbr"].astype(str)
    invalid_state_abbr = ~state_abbr.isin(STATE_ABBR_TO_FIPS)
    if invalid_state_abbr.any():
        errors.append(_sample_error("Unsupported state abbreviations", frame.loc[invalid_state_abbr, "state_abbr"]))

    for column in FRACTION_COLUMNS:
        _validate_numeric_bounds(frame, column, 0, 1, errors)

    priority_columns = [column for column in frame.columns if column.endswith("_priority")]
    for column in [*SCORE_COMPONENT_COLUMNS, *priority_columns]:
        if column in frame:
            _validate_numeric_bounds(frame, column, 0, 100, errors, allow_missing=True)

    substantive = pd.to_numeric(frame["substantive_component_coverage"], errors="coerce")
    score = pd.to_numeric(frame["support_priority_signal"], errors="coerce")
    missing_score_with_coverage = score.isna() & substantive.gt(0)
    if missing_score_with_coverage.any():
        errors.append(
            _sample_error(
                "Missing Support Priority Signal despite substantive coverage",
                frame.loc[missing_score_with_coverage, "fips"],
            )
        )

    coverage = pd.to_numeric(frame["score_component_coverage"], errors="coerce")
    lower_than_substantive = coverage.lt(substantive)
    if lower_than_substantive.any():
        errors.append(
            _sample_error(
                "Score component coverage below substantive component coverage",
                frame.loc[lower_than_substantive, "fips"],
            )
        )

    completeness = pd.to_numeric(frame["data_completeness"], errors="coerce")
    expected_grades = completeness.map(_expected_grade)
    grade_mismatches = frame["data_quality_grade"].ne(expected_grades)
    if grade_mismatches.any():
        errors.append(_sample_error("Data quality grade mismatches", frame.loc[grade_mismatches, "fips"]))

    if errors:
        raise ValueError("; ".join(errors))

    for record in frame[PUBLIC_EXPORT_REQUIRED_COLUMNS].to_dict(orient="records"):
        CountyRecord.model_validate(_clean_record(record))


def _validate_numeric_bounds(
    frame: pd.DataFrame,
    column: str,
    lower: float,
    upper: float,
    errors: list[str],
    *,
    allow_missing: bool = False,
) -> None:
    values = pd.to_numeric(frame[column], errors="coerce")
    original_missing = frame[column].isna()
    invalid_numeric = values.isna() & ~original_missing
    if invalid_numeric.any():
        errors.append(_sample_error(f"Nonnumeric values in {column}", frame.loc[invalid_numeric, column]))

    if not allow_missing:
        missing = values.isna()
        if missing.any():
            errors.append(_sample_error(f"Missing values in {column}", frame.loc[missing, "fips"]))

    out_of_bounds = values.notna() & ~values.between(lower, upper)
    if out_of_bounds.any():
        errors.append(_sample_error(f"{column} outside {lower}-{upper}", frame.loc[out_of_bounds, "fips"]))


def _clean_record(record: dict[str, object]) -> dict[str, object]:
    cleaned = {}
    for key, value in record.items():
        if pd.isna(value):
            cleaned[key] = None
        elif key == "fips":
            cleaned[key] = _normalize_code(value)
        elif key == "state_fips":
            cleaned[key] = _normalize_code(value, width=2)
        elif key == "state_abbr":
            cleaned[key] = str(value).strip().upper()
        else:
            cleaned[key] = value
    return cleaned


def _normalize_code(value: object, *, width: int = 5) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    if not text.isdigit():
        return None
    return text.zfill(width)


def _expected_grade(completeness: float) -> str:
    if completeness >= 0.85:
        return "A"
    if completeness >= 0.65:
        return "B"
    if completeness >= 0.40:
        return "C"
    return "D"


def _sample_error(label: str, values: pd.Series) -> str:
    sample = ", ".join(str(value) for value in values.head(5).tolist())
    suffix = "" if len(values) <= 5 else f" and {len(values) - 5} more"
    return f"{label}: {sample}{suffix}"
