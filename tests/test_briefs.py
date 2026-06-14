import pandas as pd

from mainstreet_atlas.generate.briefs import build_brief


def test_brief_uses_cautious_language():
    brief = build_brief(
        pd.Series(
            {
                "county_name": "Cook",
                "state_abbr": "IL",
                "support_priority_signal": 62.0,
                "establishments": 1234,
                "business_employment": 5678,
                "branches_per_1000_establishments": 4.5,
                "data_quality_grade": "B",
                "missing_source_fields": "cra_small_business_loans",
            }
        )
    )
    text = " ".join(brief.signals)

    assert "local verification" in text
    assert "conversation starter" in text
    assert "not a ranking" in text
