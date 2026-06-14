from mainstreet_atlas.fetch.hud import parse_hud_state_payload


def test_parse_hud_state_payload_returns_county_two_bedroom_fmrs():
    payload = {
        "data": {
            "counties": [
                {"code": "5100199999", "Two-Bedroom": "948.0"},
                {"code": "METRO47900M47900", "Two-Bedroom": "2045"},
                {"code": "", "Two-Bedroom": "1000"},
            ]
        }
    }

    assert parse_hud_state_payload(payload) == [
        {"fips": "51001", "two_bedroom_fmr": 948.0},
    ]
