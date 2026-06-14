from pathlib import Path

from mainstreet_atlas.constants import PROHIBITED_PUBLIC_LANGUAGE
from mainstreet_atlas.fetch.common import source_record
from mainstreet_atlas.paths import PROCESSED_DIR

PUBLIC_COPY_PATHS = [
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path("CODE_OF_CONDUCT.md"),
    Path("CHANGELOG.md"),
    Path("SECURITY.md"),
    Path("SUPPORT.md"),
    Path("GOVERNANCE.md"),
    *Path("docs").glob("*.md"),
    *Path(".github").glob("*.md"),
    *Path(".github/ISSUE_TEMPLATE").glob("*.yml"),
    *Path("site/templates").glob("*.html"),
]

RELEASE_PLACEHOLDER_PHRASES = [
    "[add link]",
    "YOUR_ORG",
    "GitHub Pages URL placeholder",
    "Screenshot placeholder",
    "lorem ipsum",
    "TODO",
    "FIXME",
    "TBD",
    "coming soon",
]

GEOGRAPHIC_NAME_EXCEPTIONS = {
    ("site/dist/counties/20017.html", "Chase"),
    ("site/dist/counties/31029.html", "Chase"),
}


def test_public_copy_avoids_prohibited_language():
    paths = [path for path in PUBLIC_COPY_PATHS if path.exists()]
    generated_dist = Path("site/dist")
    if generated_dist.exists():
        paths.extend(generated_dist.glob("*.html"))
        for fips in ["17031", "20017", "31029"]:
            county_page = generated_dist / "counties" / f"{fips}.html"
            if county_page.exists():
                paths.append(county_page)

    violations: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for phrase in PROHIBITED_PUBLIC_LANGUAGE:
            if phrase.lower() in text.lower():
                normalized = path.as_posix()
                if (normalized, phrase) not in GEOGRAPHIC_NAME_EXCEPTIONS:
                    violations.append(f"{path}: {phrase}")

    assert violations == []


def test_release_copy_has_no_unresolved_placeholders():
    paths = [
        Path("README.md"),
        Path("CONTRIBUTING.md"),
        Path("CHANGELOG.md"),
        Path("SECURITY.md"),
        Path("SUPPORT.md"),
        Path("GOVERNANCE.md"),
        *Path("docs").glob("*.md"),
        *Path(".github").glob("*.md"),
        *Path("site/templates").glob("*.html"),
    ]

    violations: list[str] = []
    for path in [path for path in paths if path.exists()]:
        text = path.read_text(encoding="utf-8")
        for phrase in RELEASE_PLACEHOLDER_PHRASES:
            if phrase.lower() in text.lower():
                violations.append(f"{path}: {phrase}")

    assert violations == []


def test_readme_includes_launch_preview_and_demo_status():
    readme = Path("README.md").read_text(encoding="utf-8")
    preview = Path("docs/assets/homepage-preview.png")

    assert "## Live Demo" in readme
    assert "GitHub Pages" in readme
    assert "http://localhost:8000/index.html" in readme
    assert "## Site Preview" in readme
    assert "docs/assets/homepage-preview.png" in readme
    assert preview.exists()
    assert preview.stat().st_size > 100_000


def test_repository_health_docs_route_sensitive_reports():
    readme = Path("README.md").read_text(encoding="utf-8")
    contributing = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
    governance = Path("GOVERNANCE.md").read_text(encoding="utf-8")
    security = Path("SECURITY.md").read_text(encoding="utf-8")
    support = Path("SUPPORT.md").read_text(encoding="utf-8")

    assert "[GOVERNANCE.md](GOVERNANCE.md)" in readme
    assert "[GOVERNANCE.md](GOVERNANCE.md)" in contributing
    assert "[SECURITY.md](SECURITY.md)" in readme
    assert "[SUPPORT.md](SUPPORT.md)" in readme
    assert "[SECURITY.md](SECURITY.md)" in contributing
    assert "[SUPPORT.md](SUPPORT.md)" in contributing
    assert "Methodology Changes" in governance
    assert "Source Changes" in governance
    assert "Release Process" in governance
    assert "Independence" in governance
    assert "Do not open a public issue" in security
    assert "Do not contribute" in security
    assert "Security or sensitive data concern" in support


def test_reuse_docs_include_citation_and_attribution_guidance():
    readme = Path("README.md").read_text(encoding="utf-8")
    citation = Path("CITATION.cff").read_text(encoding="utf-8")
    attribution = Path("docs/attribution.md").read_text(encoding="utf-8")
    sources_template = Path("site/templates/sources.html").read_text(encoding="utf-8")

    assert "[CITATION.cff](CITATION.cff)" in readme
    assert "[docs/attribution.md](docs/attribution.md)" in readme
    assert 'title: "Main Street Capital Access Atlas"' in citation
    assert 'license: "MIT"' in citation
    assert "source_manifest.json" in attribution
    assert "OpenStreetMap" in attribution
    assert "Attribution and citation" in sources_template
    assert "Source publishers do not endorse" in sources_template


def test_generated_artifact_guidance_is_present():
    contributing = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
    release_checklist = Path("docs/release_checklist.md").read_text(encoding="utf-8")
    generated_docs = Path("docs/generated_artifacts.md").read_text(encoding="utf-8")
    attributes = Path(".gitattributes").read_text(encoding="utf-8")

    for path in ["data/raw/", "data/processed/", "data/public/", "site/dist/"]:
        assert path in generated_docs

    assert "[docs/generated_artifacts.md](docs/generated_artifacts.md)" in contributing
    assert "docs/generated_artifacts.md" in release_checklist
    assert "data/public/** linguist-generated=true" in attributes
    assert "site/dist/** linguist-generated=true" in attributes
    assert "site/templates/** linguist-generated=false" in attributes


def test_accessibility_statement_is_published_and_linked():
    readme = Path("README.md").read_text(encoding="utf-8")
    contributing = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
    support = Path("SUPPORT.md").read_text(encoding="utf-8")
    accessibility_docs = Path("docs/accessibility.md").read_text(encoding="utf-8")
    accessibility_issue_template = Path(".github/ISSUE_TEMPLATE/accessibility.yml").read_text(
        encoding="utf-8"
    )
    accessibility_template = Path("site/templates/accessibility.html").read_text(encoding="utf-8")
    base_template = Path("site/templates/base.html").read_text(encoding="utf-8")

    assert "[docs/accessibility.md](docs/accessibility.md)" in readme
    assert "docs/accessibility.md" in support
    assert "Accessibility issues should identify" in contributing
    assert "Accessibility issue" in support
    assert "Current Commitments" in accessibility_docs
    assert "Report An Accessibility Issue" in accessibility_docs
    assert "name: Accessibility issue" in accessibility_issue_template
    assert "Keyboard navigation or focus" in accessibility_issue_template
    assert "assistive technology" in accessibility_issue_template
    assert "Do not include private, sensitive" in accessibility_issue_template
    assert "Non-map alternatives" in accessibility_template
    assert "Report an accessibility issue" in accessibility_template
    assert "accessibility.html" in base_template


def test_changelog_documents_initial_release_candidate():
    readme = Path("README.md").read_text(encoding="utf-8")
    release_checklist = Path("docs/release_checklist.md").read_text(encoding="utf-8")
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")

    assert "[CHANGELOG.md](CHANGELOG.md)" in readme
    assert "Update `CHANGELOG.md`" in release_checklist
    assert "## 0.1.0 - Initial Public Release Candidate" in changelog
    assert "3,235 counties and county-equivalent records" in changelog
    assert "`python -m pytest` passed with 52 tests" in changelog
    assert "External Release Gates" in changelog
    assert "GitHub Pages must be enabled" in changelog


def test_source_manifest_paths_are_repository_relative():
    record = source_record(
        source_id="example",
        dataset_name="Example",
        publisher="Example publisher",
        access_method="Example access",
        status="available",
        coverage="Example coverage",
        known_limitations="Example limitations",
        local_path=PROCESSED_DIR / "example.csv",
        fetched=True,
    )

    assert record["local_path"] == "data/processed/example.csv"
    assert "C:\\" not in record["local_path"]
