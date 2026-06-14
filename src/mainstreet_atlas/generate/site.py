"""Generate the static GitHub Pages site."""

from __future__ import annotations

import json
import logging
import math
import shutil
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from mainstreet_atlas.config import get_settings
from mainstreet_atlas.constants import ILLINOIS_FOCUS_FIPS
from mainstreet_atlas.generate.briefs import build_brief
from mainstreet_atlas.generate.charts import score_band_counts
from mainstreet_atlas.generate.data_package import (
    DATA_PACKAGE_MANIFEST,
    PUBLIC_DATA_PACKAGE_FILES,
)
from mainstreet_atlas.generate.source_manifest import read_manifest
from mainstreet_atlas.paths import (
    DIST_DIR,
    PROCESSED_DIR,
    PUBLIC_DATA_DIR,
    STATIC_DIR,
    TEMPLATE_DIR,
)
from mainstreet_atlas.transform.indicators import fmt_number, fmt_pct

LOGGER = logging.getLogger(__name__)


def generate_site() -> None:
    counties_path = PROCESSED_DIR / "county_indicators.csv"
    if not counties_path.exists():
        msg = f"Processed county indicators not found: {counties_path}. Run `make build` first."
        raise FileNotFoundError(msg)

    _reset_dist()
    env = _environment()
    settings = get_settings()
    counties = pd.read_csv(counties_path, dtype={"fips": str})
    counties["fips"] = counties["fips"].astype(str).str.zfill(5)
    counties = counties.sort_values(
        ["support_priority_signal", "state_abbr", "county_name"], ascending=[False, True, True]
    )
    manifest = read_manifest()

    _copy_assets()
    _copy_public_data()

    top_counties = counties.head(25).to_dict(orient="records")
    illinois = counties[counties["state_abbr"] == "IL"].copy()
    focus = illinois[illinois["fips"].isin(ILLINOIS_FOCUS_FIPS)].copy()
    if focus.empty:
        focus = illinois.head(12)
    else:
        focus = focus.sort_values(["support_priority_signal"], ascending=False)

    common = {
        "site_title": "Main Street Capital Access Atlas",
        "source_manifest": manifest,
        "fmt_number": fmt_number,
        "fmt_pct": fmt_pct,
        "fmt_text": _fmt_text,
        "fmt_year": _fmt_year,
        "asset_path": "",
        "css_version": _asset_hash("css/styles.css"),
        "js_version": _asset_hash("js/app.js"),
        "social_image_url": _absolute_url(settings.site_url, "static/img/social-preview.png"),
    }
    _render(
        env,
        "index.html",
        DIST_DIR / "index.html",
        {
            **common,
            "active": "home",
            "canonical_url": _absolute_url(settings.site_url, "index.html"),
            "counties": counties,
            "top_counties": top_counties,
            "illinois_focus": focus.to_dict(orient="records"),
            "score_bands": score_band_counts(counties),
        },
    )
    _render(
        env,
        "illinois.html",
        DIST_DIR / "illinois.html",
        {
            **common,
            "active": "illinois",
            "canonical_url": _absolute_url(settings.site_url, "illinois.html"),
            "illinois_counties": illinois.to_dict(orient="records"),
            "illinois_focus": focus.to_dict(orient="records"),
        },
    )
    for template_name, output_name, active in [
        ("methodology.html", "methodology.html", "methodology"),
        ("limitations.html", "limitations.html", "limitations"),
        ("sources.html", "sources.html", "sources"),
        ("contribute.html", "contribute.html", "contribute"),
        ("accessibility.html", "accessibility.html", "accessibility"),
        ("404.html", "404.html", "not-found"),
    ]:
        _render(
            env,
            template_name,
            DIST_DIR / output_name,
            {
                **common,
                "active": active,
                "canonical_url": _absolute_url(settings.site_url, output_name),
                "counties": counties,
                "top_counties": top_counties,
                "score_bands": score_band_counts(counties),
            },
        )

    county_dir = DIST_DIR / "counties"
    county_dir.mkdir(parents=True, exist_ok=True)
    county_records = counties.to_dict(orient="records")
    for record in county_records:
        brief = build_brief(record)
        _render(
            env,
            "county.html",
            county_dir / f"{record['fips']}.html",
            {
                **common,
                "asset_path": "../",
                "active": "county",
                "canonical_url": _absolute_url(settings.site_url, f"counties/{record['fips']}.html"),
                "county": record,
                "brief": brief,
            },
        )

    _write_search_index(county_records)
    _write_nojekyll()
    _write_robots_txt(settings.site_url)
    if settings.site_url:
        _write_sitemap(county_records, settings.site_url)
    LOGGER.info("Generated %s county pages in %s", len(county_records), DIST_DIR)


def _environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["json"] = lambda value: json.dumps(_clean_json(value))
    env.filters["county_url"] = lambda fips: f"counties/{str(fips).zfill(5)}.html"
    env.filters["score"] = _fmt_score
    return env


def _render(env: Environment, template: str, destination: Path, context: dict[str, Any]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    html = env.get_template(template).render(**context)
    destination.write_text(html, encoding="utf-8")


def _reset_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def _copy_assets() -> None:
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, DIST_DIR / "static", dirs_exist_ok=True)


def _asset_hash(relative_path: str) -> str:
    source = STATIC_DIR / relative_path
    if not source.exists():
        return "missing"
    return sha256(source.read_bytes()).hexdigest()[:12]


def _copy_public_data() -> None:
    target = DIST_DIR / "assets" / "data"
    target.mkdir(parents=True, exist_ok=True)
    for file_name in [*PUBLIC_DATA_PACKAGE_FILES, DATA_PACKAGE_MANIFEST]:
        source = PUBLIC_DATA_DIR / file_name
        if source.exists():
            shutil.copy2(source, target / source.name)


def _write_search_index(records: list[dict[str, Any]]) -> None:
    index = [
        {
            "fips": record["fips"],
            "county_name": record["county_name"],
            "state_abbr": record["state_abbr"],
            "state_name": record.get("state_name"),
            "support_priority_signal": record.get("support_priority_signal"),
            "data_quality_grade": record.get("data_quality_grade"),
            "establishments": record.get("establishments"),
            "branch_count": record.get("branch_count"),
            "branches_per_10k_residents": record.get("branches_per_10k_residents"),
            "branches_per_1000_establishments": record.get("branches_per_1000_establishments"),
            "poverty_pct": record.get("poverty_pct"),
            "median_household_income": record.get("median_household_income"),
            "url": f"counties/{record['fips']}.html",
        }
        for record in records
    ]
    (DIST_DIR / "assets" / "data" / "county-search.json").write_text(
        json.dumps(_clean_json(index), indent=2),
        encoding="utf-8",
    )


def _write_robots_txt(site_url: str | None) -> None:
    lines = ["User-agent: *", "Allow: /"]
    if site_url:
        lines.append(f"Sitemap: {urljoin(site_url, 'sitemap.xml')}")
    (DIST_DIR / "robots.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_nojekyll() -> None:
    (DIST_DIR / ".nojekyll").write_text("", encoding="utf-8")


def _write_sitemap(records: list[dict[str, Any]], site_url: str) -> None:
    urls = [
        "index.html",
        "illinois.html",
        "methodology.html",
        "limitations.html",
        "sources.html",
        "contribute.html",
        "accessibility.html",
        *[f"counties/{record['fips']}.html" for record in records],
    ]
    body = "\n".join(
        "\n".join(
            [
                "  <url>",
                f"    <loc>{_xml_escape(urljoin(site_url, url))}</loc>",
                "  </url>",
            ]
        )
        for url in urls
    )
    payload = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )
    (DIST_DIR / "sitemap.xml").write_text(payload, encoding="utf-8")


def _absolute_url(site_url: str | None, path: str) -> str | None:
    if not site_url:
        return None
    return urljoin(site_url, path)


def _fmt_score(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "Unavailable"
    if math.isnan(numeric):
        return "Unavailable"
    return f"{numeric:.1f}"


def _fmt_year(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "Unavailable"
    if math.isnan(numeric):
        return "Unavailable"
    return str(int(numeric))


def _fmt_text(value: object) -> str:
    if value is None:
        return "Unavailable"
    if isinstance(value, float) and math.isnan(value):
        return "Unavailable"
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return "Unavailable"
    return text


def _clean_json(value: Any) -> Any:
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {key: _clean_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean_json(item) for item in value]
    return value


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
