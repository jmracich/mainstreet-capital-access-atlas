from mainstreet_atlas.transform.clean import ensure_fips


def test_ensure_fips_is_five_digits():
    values = ensure_fips(__import__("pandas").Series([17031, "101", "06037"]))

    assert values.tolist() == ["17031", "00101", "06037"]
