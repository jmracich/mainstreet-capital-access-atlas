from mainstreet_atlas.constants import PROHIBITED_PUBLIC_LANGUAGE
from mainstreet_atlas.generate.briefs import build_brief


def test_generated_brief_avoids_prohibited_public_language():
    brief = build_brief(
        {
            "county_name": "Example",
            "state_abbr": "IL",
            "support_priority_signal": 50,
            "data_quality_grade": "C",
            "missing_source_fields": "sba_loan_count",
        }
    )
    text = " ".join([brief.title, *brief.signals, *brief.questions, *brief.starting_points])

    for phrase in PROHIBITED_PUBLIC_LANGUAGE:
        assert phrase.lower() not in text.lower()
