"""Generate cautious county-level Main Street Opportunity Brief content."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pandas as pd

from mainstreet_atlas.transform.indicators import fmt_number, fmt_pct

QUESTIONS_TO_ASK = [
    "What types of businesses are struggling most to access affordable capital or coaching?",
    "Are business owners aware of CDFIs, SBDCs, chambers, SCORE, or other local resources?",
    "Are language, transportation, digital access, or documentation barriers affecting participation?",
    "Are there local procurement or anchor-institution opportunities that could support small firms?",
    "Which existing organizations are already trusted by business owners?",
]

STARTING_POINTS = [
    "Host a capital-readiness workshop with local partners.",
    "Build a local resource guide for entrepreneurs.",
    "Connect businesses to CDFIs, SBDCs, SCORE chapters, chambers, and other support organizations.",
    "Help entrepreneurs understand cash-flow basics and documentation needs.",
    "Coordinate with libraries, community colleges, faith communities, and local institutions.",
    "Support buy-local or procurement-readiness efforts where local partners see demand.",
]


@dataclass(frozen=True)
class CountyBrief:
    title: str
    signals: list[str]
    questions: list[str]
    starting_points: list[str]
    limitations: str


def build_brief(row: pd.Series | dict[str, Any]) -> CountyBrief:
    data = row if isinstance(row, dict) else row.to_dict()
    county = data.get("county_name", "This county")
    state = data.get("state_abbr", "")
    title = f"Main Street Opportunity Brief: {county}, {state}"
    signals = _signals(data)
    if len(signals) < 3:
        signals.extend(_fallback_signals(data, needed=3 - len(signals)))
    return CountyBrief(
        title=title,
        signals=signals[:5],
        questions=QUESTIONS_TO_ASK,
        starting_points=STARTING_POINTS,
        limitations=(
            "Public data is lagged, incomplete, and uneven across geographies. These signals should "
            "be verified with local residents, business owners, and community organizations before "
            "drawing conclusions or choosing interventions."
        ),
    )


def _signals(data: dict[str, Any]) -> list[str]:
    signals: list[str] = []

    score = _num(data.get("support_priority_signal"))
    if score is not None:
        signals.append(
            f"The public-data Support Priority Signal is {score:.1f} out of 100. Treat this as a conversation starter for local verification, not a ranking of community value."
        )

    establishments = _num(data.get("establishments"))
    employment = _num(data.get("business_employment"))
    if establishments is not None:
        if employment is not None:
            signals.append(
                f"County Business Patterns reports {fmt_number(establishments)} establishments and {fmt_number(employment)} paid employees, suggesting small employers are an important part of the local economic picture."
            )
        else:
            signals.append(
                f"County Business Patterns reports {fmt_number(establishments)} establishments, which may be useful context for local small-business support planning."
            )

    branches_per_est = _num(data.get("branches_per_1000_establishments"))
    if branches_per_est is not None:
        signals.append(
            f"FDIC branch data suggests about {branches_per_est:.1f} branches per 1,000 establishments. Local partners can verify whether branch presence translates into useful capital-navigation support."
        )

    poverty = _num(data.get("poverty_pct"))
    unemployment = _num(data.get("unemployment_pct"))
    if poverty is not None or unemployment is not None:
        parts = []
        if poverty is not None:
            parts.append(f"a poverty signal of {fmt_pct(poverty)}")
        if unemployment is not None:
            parts.append(f"an unemployment signal of {fmt_pct(unemployment)}")
        signals.append(
            f"Economic-stress context includes {' and '.join(parts)}. These household-level indicators should be interpreted carefully and verified locally."
        )

    rent_burden = _num(data.get("rent_burden_pct"))
    if rent_burden is not None:
        signals.append(
            f"ACS rent data suggests {fmt_pct(rent_burden)} of renter households are cost-burdened, which may affect business-owner and worker household stability."
        )

    missing = str(data.get("missing_source_fields") or "").strip()
    grade = data.get("data_quality_grade")
    if missing:
        signals.append(
            f"The data quality grade is {grade}. Missing or unavailable fields should be filled through official sources or local partner knowledge before making decisions."
        )

    return signals


def _fallback_signals(data: dict[str, Any], needed: int) -> list[str]:
    grade = data.get("data_quality_grade", "D")
    fallback = [
        f"The data quality grade is {grade}, so the strongest next step is to verify source coverage before drawing conclusions.",
        "Available public data may help identify where local listening, resource mapping, or capital-navigation support could be useful.",
        "Local partners should compare these signals with lived experience, trusted organizations, and current business-owner needs.",
    ]
    return fallback[:needed]


def _num(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number):
        return None
    return number
