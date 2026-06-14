"""Validation helpers for user-supplied county CSV imports."""

from __future__ import annotations

import pandas as pd


def prepare_manual_county_frame(
    frame: pd.DataFrame,
    *,
    source_label: str,
    required_columns: set[str],
    optional_columns: list[str],
) -> pd.DataFrame:
    required = {"fips", *required_columns}
    allowed = ["fips", *sorted(required_columns), *optional_columns]
    missing = required - set(frame.columns)
    if missing:
        msg = f"Manual {source_label} file is missing columns: {', '.join(sorted(missing))}"
        raise ValueError(msg)

    extra = sorted(set(frame.columns) - set(allowed))
    if extra:
        msg = (
            f"Manual {source_label} file contains unsupported columns: {', '.join(extra)}. "
            "Keep source notes in the pull request or documentation, not the county CSV."
        )
        raise ValueError(msg)

    output = frame.copy()
    output["fips"] = output["fips"].map(_normalize_fips)
    invalid_fips = output["fips"].isna()
    if invalid_fips.any():
        msg = f"Manual {source_label} file contains invalid five-digit county FIPS values"
        raise ValueError(msg)
    if output["fips"].duplicated().any():
        duplicates = ", ".join(sorted(output.loc[output["fips"].duplicated(), "fips"].unique()))
        msg = f"Manual {source_label} file contains duplicate county FIPS values: {duplicates}"
        raise ValueError(msg)

    for column in [*sorted(required_columns), *optional_columns]:
        if column not in output.columns:
            output[column] = pd.NA
        before = output[column].copy()
        output[column] = pd.to_numeric(output[column], errors="coerce")
        invalid_numeric = before.notna() & before.astype(str).str.strip().ne("") & output[column].isna()
        if invalid_numeric.any():
            msg = f"Manual {source_label} file contains nonnumeric values in {column}"
            raise ValueError(msg)

    return output[allowed]


def _normalize_fips(value: object) -> str | None:
    text = "" if value is None else str(value).strip()
    text = text.replace(".0", "") if text.endswith(".0") else text
    if not text.isdigit() or len(text) > 5:
        return None
    return text.zfill(5)
