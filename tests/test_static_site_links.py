import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

import pytest


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)


def _representative_html_paths(root: Path) -> list[Path]:
    paths = list(root.glob("*.html"))
    for fips in ["01001", "06037", "17031", "20017", "31029", "36061", "48201"]:
        county_page = root / "counties" / f"{fips}.html"
        if county_page.exists():
            paths.append(county_page)
    return paths


def test_representative_static_site_links_resolve():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    root_resolved = root.resolve()
    missing: list[str] = []
    for html_path in _representative_html_paths(root):
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))

        for link in parser.links:
            parsed = urlparse(link)
            if parsed.scheme or parsed.netloc or parsed.path == "" or link.startswith("#"):
                continue

            if parsed.path.startswith("/"):
                target = root / unquote(parsed.path.lstrip("/"))
            else:
                target = html_path.parent / unquote(parsed.path)

            try:
                target.resolve().relative_to(root_resolved)
            except ValueError:
                missing.append(f"{html_path}: {link} escapes site/dist")
                continue

            if not target.exists():
                missing.append(f"{html_path}: {link}")

    assert missing == []


def test_generated_map_popup_exposes_required_context():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    app_js = root / "static" / "js" / "app.js"
    county_map = root / "assets" / "data" / "county-map.geojson"

    assert "CRA signal" in app_js.read_text(encoding="utf-8")
    assert "cra_small_business_loans" in app_js.read_text(encoding="utf-8")
    assert "cra_loans_per_1000_establishments" in app_js.read_text(encoding="utf-8")

    payload = county_map.read_text(encoding="utf-8")
    assert "cra_small_business_loans" in payload
    assert "cra_loans_per_1000_establishments" in payload


def test_map_payload_matches_visible_choropleth_contract():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    county_map = root / "assets" / "data" / "county-map.geojson"
    counties_csv = root / "assets" / "data" / "counties.csv"
    payload = json.loads(county_map.read_text(encoding="utf-8"))
    features = payload["features"]
    states = {feature["properties"]["state_abbr"] for feature in features}
    required_properties = {
        "fips",
        "county_name",
        "state_abbr",
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
    }
    excluded_states = {"AK", "HI", "AS", "GU", "MP", "PR", "VI"}

    county_export_rows = sum(1 for _ in counties_csv.open(encoding="utf-8")) - 1

    assert payload["type"] == "FeatureCollection"
    assert len(features) < county_export_rows
    assert states.isdisjoint(excluded_states)
    assert all(set(feature["properties"]) == required_properties for feature in features)


def test_generated_site_includes_robots_txt():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    robots = root / "robots.txt"

    assert robots.exists()
    text = robots.read_text(encoding="utf-8")
    assert "User-agent: *" in text
    assert "Allow: /" in text


def test_generated_site_includes_github_pages_hardening_files():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    nojekyll = root / ".nojekyll"
    not_found = root / "404.html"
    html = not_found.read_text(encoding="utf-8")

    assert nojekyll.exists()
    assert nojekyll.read_text(encoding="utf-8") == ""
    assert not_found.exists()
    assert "Page not found" in html
    assert 'href="index.html#explore"' in html
    assert "credit model" in html


def test_homepage_includes_score_distribution_chart():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    homepage = root / "index.html"
    html = homepage.read_text(encoding="utf-8")

    assert "Score calibration" in html
    assert 'class="distribution-table"' in html
    assert html.count('class="distribution-row"') == 4


def test_homepage_uses_civic_design_scaffold():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    homepage = root / "index.html"
    html = homepage.read_text(encoding="utf-8")
    css = (root / "static" / "css" / "styles.css").read_text(encoding="utf-8")
    js = (root / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert 'href="index.html#explore"' in html
    assert 'class="workspace-header"' in html
    assert 'class="workspace-links"' not in html
    assert 'class="utility-link"' not in html
    assert 'class="hero compact-hero"' not in html
    assert 'class="status-strip"' not in html
    assert 'id="explore"' in html
    assert 'id="county-table"' in html
    assert 'id="selected-county"' in html
    assert 'aria-describedby="map-alt-note"' in html
    assert "See where Main Street support may need attention" in html
    assert "Local civic, CDFI, chamber, philanthropy" in html
    assert "80+ means" in html
    assert "An 80 is not a grade" in html
    assert "80-100" in html
    assert "High follow-up" in html
    assert "Darker color means a stronger public-data support signal" in html
    assert 'class="score-primer"' in html
    assert 'class="score-band-list"' in html
    assert "not to rank communities or make credit decisions" in html
    assert "Prefer a table?" in html
    assert "<noscript>" in html
    assert "Map alternative" in html
    assert "County-level MVP" not in html
    assert "hero-panel" not in html
    assert "static/css/styles.css?v=" in html
    assert "static/js/app.js?v=" in html
    assert "linear-gradient" not in css
    assert "renderSelectedCounty" in js
    assert "signalBand" in js
    assert "High follow-up" in js
    assert "fitInitialMapView" in js
    assert "initialMapMinZoom" in js
    assert "window.innerWidth < 760 ? 3 : 4" not in js


def test_county_search_index_supports_state_name_and_preview_metrics():
    root = Path("site/dist")
    if not root.exists():
        pytest.skip("Generated site is not present.")

    search_index = json.loads((root / "assets" / "data" / "county-search.json").read_text(encoding="utf-8"))
    app_js = (root / "static" / "js" / "app.js").read_text(encoding="utf-8")
    cook = next(record for record in search_index if record["fips"] == "17031")
    required_fields = {
        "fips",
        "county_name",
        "state_abbr",
        "state_name",
        "support_priority_signal",
        "data_quality_grade",
        "establishments",
        "branch_count",
        "branches_per_10k_residents",
        "branches_per_1000_establishments",
        "poverty_pct",
        "median_household_income",
        "url",
    }

    assert len(search_index) == 3235
    assert set(cook) == required_fields
    assert cook["state_name"] == "Illinois"
    assert cook["establishments"] is not None
    assert cook["branches_per_10k_residents"] is not None
    assert "state_name" in app_js
