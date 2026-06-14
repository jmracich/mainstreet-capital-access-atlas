# Changelog

All notable project changes should be documented here. This project follows a practical release-note format for public civic-data work: what changed, what was verified, what data sources are included, and which release gates remain external.

## Unreleased

- No unreleased changes have been tagged yet.

## 0.1.0 - Initial Public Release Candidate

### Added

- National county-level public dataset covering 3,235 counties and county-equivalent records.
- Static GitHub Pages-compatible website generated into `site/dist/`.
- Homepage county choropleth, county search, selected-county summary panel, non-map alternatives, and downloadable public data.
- Illinois spotlight page with curated county groups for the first launch focus.
- Static Main Street Opportunity Brief pages for every generated county and county-equivalent record.
- Methodology, limitations, sources, contribute, accessibility, and custom 404 pages.
- Public data package with CSV, JSON, contiguous-U.S. map GeoJSON, source manifest, generated data dictionary, and checksum manifest.
- Modular public-data adapters for Census, FDIC, optional ACS, optional HUD, and manual BLS/CRA/SBA/CDFI county imports.
- Transparent Small Business Support Priority Signal with winsorized normalization, explicit directionality, missing-data handling, score-component coverage, and data-quality grades.
- GitHub Actions workflows for CI, scheduled/manual public-data refresh, and GitHub Pages deployment.
- Open-source project health docs: contributing guide, code of conduct, security policy, support guide, governance, citation, attribution, generated-artifact guidance, release checklist, and launch-post draft.

### Verified Locally

- `python -m mainstreet_atlas.cli all` generated the public dataset and static site.
- `python -m pytest` passed with 52 tests.
- `python -m ruff check .` passed.
- `site/dist` contains a deployable static site with `404.html`, `.nojekyll`, `robots.txt`, top-level pages, and 3,235 generated county brief pages.
- Browser smoke checks verified desktop and mobile layout, map rendering, search behavior, selected-county preview metrics, and no console warnings or horizontal overflow in checked flows.

### Source Status

- Automated in the default build: Census county cartographic boundaries, Census County Business Patterns, Census Population Estimates Program, Census SAIPE, FDIC BankFind branch locations, and FDIC Summary of Deposits.
- Optional token source: Census ACS 5-year API with `CENSUS_API_KEY`.
- Manual or optional imports: BLS LAUS, FFIEC CRA small-business lending, SBA lending, certified CDFI counts, and HUD Fair Market Rents / Income Limits.

### External Release Gates

- A Git remote is not configured in the local workspace, so GitHub-hosted CI and Pages deployment still need to be verified after push.
- GitHub Pages must be enabled with GitHub Actions as the source.
- Public repository and live-site URLs should be added to launch copy after deployment.
