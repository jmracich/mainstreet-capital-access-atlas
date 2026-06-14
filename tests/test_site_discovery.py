from pathlib import Path

from mainstreet_atlas.generate import site


def test_sitemap_and_robots_use_configured_site_url(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(site, "DIST_DIR", tmp_path)

    site._write_robots_txt("https://example.org/main-street-capital-access-atlas/")
    site._write_sitemap(
        [{"fips": "17031"}, {"fips": "01001"}],
        "https://example.org/main-street-capital-access-atlas/",
    )

    robots = (tmp_path / "robots.txt").read_text(encoding="utf-8")
    sitemap = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")

    assert "Sitemap: https://example.org/main-street-capital-access-atlas/sitemap.xml" in robots
    assert "<loc>https://example.org/main-street-capital-access-atlas/index.html</loc>" in sitemap
    assert (
        "<loc>https://example.org/main-street-capital-access-atlas/counties/17031.html</loc>"
        in sitemap
    )
    assert (
        "<loc>https://example.org/main-street-capital-access-atlas/counties/01001.html</loc>"
        in sitemap
    )
    assert (
        "<loc>https://example.org/main-street-capital-access-atlas/accessibility.html</loc>"
        in sitemap
    )


def test_absolute_url_helper_respects_configured_site_url():
    assert (
        site._absolute_url(
            "https://example.org/main-street-capital-access-atlas/",
            "static/img/social-preview.png",
        )
        == "https://example.org/main-street-capital-access-atlas/static/img/social-preview.png"
    )
    assert site._absolute_url(None, "static/img/social-preview.png") is None
