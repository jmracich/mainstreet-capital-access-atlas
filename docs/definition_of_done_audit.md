# Definition of Done Audit

Last reviewed: 2026-06-11

This audit tracks the current evidence for the original project brief. It is meant to help maintainers distinguish verified release readiness from external publication steps that still depend on repository hosting.

## Verified Locally

- `python -m mainstreet_atlas.cli all` completed successfully and generated the full public dataset and static site.
- `python -m pytest` passed with 53 tests.
- `python -m ruff check .` passed.
- `site/dist` contains a deployable static site.
- `site/dist` includes `404.html` and `.nojekyll` for GitHub Pages static hosting.
- `site/dist/robots.txt` is generated for crawler discovery; `sitemap.xml` is generated when `SITE_URL` is configured.
- `site/dist/counties/` contains 3,235 generated county and county-equivalent brief pages.
- `data/public/counties.csv` contains 3,235 rows and 86 documented public columns.
- `data/public/data_dictionary.csv` covers every county export column in order.
- `data/public/data_package_manifest.json` records published data file sizes, row or feature counts, and SHA-256 checksums.
- `data/public/source_manifest.json` contains 12 tracked source records.
- `docs/data_sources.md` covers every source id, dataset name, and publisher in the generated source manifest.
- Public county exports are validated during the build for required columns, duplicate FIPS rows, valid state/FIPS alignment, score ranges, coverage ranges, score availability, and data-quality grade consistency.
- `site/dist/assets/data/` publishes only the intended public data package files plus the compact county search index; hidden repository placeholders and legacy duplicate GeoJSON files are excluded.
- `site/dist/assets/data/county-map.geojson` is scoped to the contiguous-U.S. homepage choropleth, contains 3,109 rendered map features, excludes non-rendered states and territories, and carries only popup-relevant public properties.
- Manual source adapters reject unsupported columns, duplicate FIPS rows, invalid county FIPS values, and nonnumeric measure values before data can enter the public export.
- Local HTTP checks returned `200` for the homepage, county pages, and public data assets.
- Browser checks passed for desktop and mobile layouts with no console warnings or errors in the verified flows.
- Browser map smoke check rendered 3,109 county paths from the homepage map asset with no map error or horizontal overflow.
- County search supports county names, state abbreviations, and full state names, including off-map county-equivalent records.
- Browser search smoke check verified full-state-name search and selected-county preview metrics for a non-contiguous county page.
- Generated pages include launch-ready Open Graph and Twitter card metadata with a static social preview image; canonical and absolute social URLs are supported when `SITE_URL` is configured.
- Front-end redesign follows `DESIGN.md`: compact hero, Explore navigation anchor, project status strip, muted civic palette, selected-county map sidebar, curated Illinois spotlight groups, printable county brief summary band, and consistent card/table/callout components.
- Homepage map section includes explicit non-map alternatives: a described map caveat, a county-table anchor, county CSV download link, and a `noscript` fallback.
- Desktop browser smoke checks passed for homepage map/search selection, Illinois spotlight groups, and a Cook County brief with no horizontal overflow or console warnings/errors.
- Mobile browser smoke checks passed for menu open/close with Escape, compact responsive layout, search/sidebar before map, 420px map height, no horizontal overflow, and no console warnings/errors.
- Static accessibility checks cover representative generated pages for landmarks, one H1, metadata, skip-link targets, and navigation ARIA.
- Mobile navigation updates `aria-expanded` and closes on Escape in browser verification.
- Homepage includes a redesigned signal-distribution table so readers can interpret county signal bands in context.
- README includes a GitHub Pages live-demo status section and a real rendered homepage preview image at `docs/assets/homepage-preview.png`.
- `SECURITY.md` and `SUPPORT.md` route sensitive reports, data issues, methodology feedback, source requests, and maintainer support boundaries.
- `CITATION.cff`, `docs/attribution.md`, and the generated Sources page document project citation, source attribution, and map attribution expectations.
- `docs/generated_artifacts.md` and `.gitattributes` distinguish source files from reproducible generated outputs and mark generated data/site directories for GitHub diff readability.
- `GOVERNANCE.md` documents decision principles, methodology-change expectations, source acceptance standards, release process, and independence rules.
- `docs/accessibility.md` and `site/dist/accessibility.html` document accessibility commitments, known constraints, non-map alternatives, testing coverage, and issue-reporting guidance.
- `.github/ISSUE_TEMPLATE/accessibility.yml` provides structured accessibility reporting fields for page/file, barrier area, observed behavior, expected behavior, environment, and privacy-safe attachments.
- `CHANGELOG.md` documents the initial public release candidate, verified local commands, source status, and external release gates.

## Source Status

Automated and available in the default build:

- Census county cartographic boundaries
- Census County Business Patterns
- Census Population Estimates Program
- Census SAIPE income and poverty estimates
- FDIC BankFind branch locations
- FDIC Summary of Deposits

Optional token source:

- Census ACS 5-year API through `CENSUS_API_KEY`

Manual or optional imports:

- BLS LAUS county unemployment
- FFIEC CRA small-business lending
- SBA lending
- Certified CDFI county counts
- HUD Fair Market Rents / Income Limits

## External Release Gates

- A Git remote is not configured in this workspace, so GitHub Pages deployment cannot be verified from local evidence.
- `make` is not installed in this Windows environment, so `make install`, `make all`, `make test`, and `make serve` cannot be executed locally here.
- `.github/workflows/ci.yml` now verifies the documented Makefile workflow on Ubuntu, where `make` is available by default.
- `.github/workflows/deploy-pages.yml` is configured to build and deploy `site/dist` through official GitHub Pages actions once the repository is pushed to GitHub and Pages is enabled.

## Remaining Release Steps

1. Push the repository to the chosen GitHub owner or organization.
2. Confirm CI passes on GitHub.
3. Enable GitHub Pages with GitHub Actions as the source.
4. Run or wait for the Pages deployment workflow.
5. Add the published repository and live-site URLs to any launch copy before posting externally.
