"""Support Priority Signal scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd

from mainstreet_atlas.transform.clean import safe_divide
from mainstreet_atlas.transform.normalize import row_mean, winsorized_percentile

COMPONENT_WEIGHTS = {
    "small_business_importance": 0.20,
    "capital_access_visibility_gap": 0.20,
    "community_economic_stress": 0.20,
    "housing_cost_pressure": 0.15,
    "local_support_ecosystem_gap": 0.15,
    "data_quality_gap": 0.10,
}

SOURCE_FIELD_GROUPS = {
    "population": ["population"],
    "business": [
        "establishments",
        "business_employment",
        "annual_payroll_thousands",
        "small_establishments_under_20_pct",
    ],
    "banking": ["branch_count", "branch_deposits_thousands"],
    "acs": [
        "median_household_income",
        "poverty_pct",
        "unemployment_pct",
        "rent_burden_pct",
        "no_vehicle_pct",
        "no_internet_pct",
    ],
    "cra": ["cra_small_business_loans"],
    "sba": ["sba_loan_count"],
    "cdfi": ["cdfi_count"],
    "hud": ["fmr_to_income_pct", "two_bedroom_fmr"],
}


def score_counties(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output = _derive_rates(output)
    output = _add_normalized_indicators(output)
    output = _add_components(output)
    output = _add_data_quality(output)
    output = _add_final_score(output)
    return output


def data_quality_grade(completeness: float) -> str:
    if completeness >= 0.85:
        return "A"
    if completeness >= 0.65:
        return "B"
    if completeness >= 0.40:
        return "C"
    return "D"


def _derive_rates(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for column in {col for cols in SOURCE_FIELD_GROUPS.values() for col in cols} | {"population"}:
        if column in output.columns:
            output[column] = pd.to_numeric(output[column], errors="coerce")

    output["establishments_per_1000_residents"] = safe_divide(
        output.get("establishments", np.nan) * 1000,
        output.get("population", np.nan),
    )
    output["employment_per_1000_residents"] = safe_divide(
        output.get("business_employment", np.nan) * 1000,
        output.get("population", np.nan),
    )
    output["branches_per_10k_residents"] = safe_divide(
        output.get("branch_count", np.nan) * 10000,
        output.get("population", np.nan),
    )
    output["branches_per_1000_establishments"] = safe_divide(
        output.get("branch_count", np.nan) * 1000,
        output.get("establishments", np.nan),
    )
    output["branch_deposits_per_resident"] = safe_divide(
        output.get("branch_deposits_thousands", np.nan) * 1000,
        output.get("population", np.nan),
    )
    output["cra_loans_per_1000_establishments"] = safe_divide(
        output.get("cra_small_business_loans", np.nan) * 1000,
        output.get("establishments", np.nan),
    )
    output["sba_loans_per_1000_establishments"] = safe_divide(
        output.get("sba_loan_count", np.nan) * 1000,
        output.get("establishments", np.nan),
    )
    output["cdfis_per_1000_establishments"] = safe_divide(
        output.get("cdfi_count", np.nan) * 1000,
        output.get("establishments", np.nan),
    )
    return output


def _add_normalized_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    specs = {
        "establishments_per_1000_residents": True,
        "employment_per_1000_residents": True,
        "establishments": True,
        "small_establishments_under_20_pct": True,
        "branches_per_10k_residents": False,
        "branches_per_1000_establishments": False,
        "cra_loans_per_1000_establishments": False,
        "sba_loans_per_1000_establishments": False,
        "poverty_pct": True,
        "unemployment_pct": True,
        "no_vehicle_pct": True,
        "no_internet_pct": True,
        "median_household_income": False,
        "rent_burden_pct": True,
        "fmr_to_income_pct": True,
        "cdfis_per_1000_establishments": False,
    }
    for column, higher_is_priority in specs.items():
        if column in output.columns:
            output[f"{column}_priority"] = winsorized_percentile(
                output[column],
                higher_is_priority=higher_is_priority,
            )
    return output


def _add_components(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output["small_business_importance"] = row_mean(
        output,
        [
            "establishments_per_1000_residents_priority",
            "employment_per_1000_residents_priority",
            "establishments_priority",
            "small_establishments_under_20_pct_priority",
        ],
    )
    output["capital_access_visibility_gap"] = row_mean(
        output,
        [
            "branches_per_10k_residents_priority",
            "branches_per_1000_establishments_priority",
            "cra_loans_per_1000_establishments_priority",
            "sba_loans_per_1000_establishments_priority",
        ],
    )
    output["community_economic_stress"] = row_mean(
        output,
        [
            "poverty_pct_priority",
            "unemployment_pct_priority",
            "no_vehicle_pct_priority",
            "no_internet_pct_priority",
            "median_household_income_priority",
        ],
    )
    output["housing_cost_pressure"] = row_mean(
        output,
        ["rent_burden_pct_priority", "fmr_to_income_pct_priority"],
    )
    output["local_support_ecosystem_gap"] = row_mean(
        output,
        ["cdfis_per_1000_establishments_priority", "branches_per_1000_establishments_priority"],
    )
    return output


def _add_data_quality(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    possible = [column for cols in SOURCE_FIELD_GROUPS.values() for column in cols]
    present_columns = [column for column in possible if column in output.columns]
    if present_columns:
        completeness = output[present_columns].notna().mean(axis=1)
    else:
        completeness = pd.Series(0.0, index=output.index)
    output["data_completeness"] = completeness.round(3)
    output["data_quality_gap"] = (1 - completeness) * 100
    output["data_quality_grade"] = completeness.map(data_quality_grade)
    output["missing_source_fields"] = output.apply(_missing_fields, axis=1, args=(present_columns,))
    return output


def _add_final_score(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    weighted_total = pd.Series(0.0, index=output.index)
    available_weight = pd.Series(0.0, index=output.index)
    substantive_available = pd.Series(0.0, index=output.index)

    for component, weight in COMPONENT_WEIGHTS.items():
        values = pd.to_numeric(output.get(component), errors="coerce")
        mask = values.notna()
        if component != "data_quality_gap":
            substantive_available = substantive_available.add(mask.astype(float) * weight, fill_value=0)
        else:
            mask = mask & (substantive_available > 0)
        weighted_total = weighted_total.add(values.fillna(0) * weight, fill_value=0)
        available_weight = available_weight.add(mask.astype(float) * weight, fill_value=0)

    score = weighted_total / available_weight.where((available_weight != 0) & (substantive_available != 0))
    output["score_component_coverage"] = available_weight.round(3)
    output["support_priority_signal"] = score.clip(0, 100).round(1)
    output["substantive_component_coverage"] = substantive_available.round(3)
    return output


def _missing_fields(row: pd.Series, columns: list[str]) -> str:
    missing = [column for column in columns if pd.isna(row.get(column))]
    return ", ".join(missing)
