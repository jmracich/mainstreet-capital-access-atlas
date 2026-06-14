# Data Sources

Main Street Capital Access Atlas uses free public data and publishes no private or sensitive data. The default build must succeed without paid APIs, credentials, manual files, a database, or a backend service.

The authoritative machine-readable inventory is `data/public/source_manifest.json`. The public website renders the same records on `site/dist/sources.html`, and the downloadable site copy is published under `site/dist/assets/data/source_manifest.json`.

## Source Status Definitions

| Status | Meaning |
| --- | --- |
| `available` | The source was fetched, parsed, or registered successfully in the current build. |
| `optional_token` | The adapter exists, but the source requires optional credentials or configuration that are not required for the default build. |
| `manual_optional` | The adapter accepts a documented county-level CSV, but no manual file is required for the default build. |
| `unavailable` | The source was attempted or registered but could not provide usable data in the current build. |

Missing optional data is exposed through missing fields, source status, score-component coverage, and county data-quality metadata. Missing official values are not filled with invented data.

## Current Source Inventory

| Source id | Dataset | Publisher | Current role | Default status |
| --- | --- | --- | --- | --- |
| `census_county_geometry` | 2023 Census Cartographic Boundary File, Counties | U.S. Census Bureau | County and county-equivalent geometry, names, FIPS codes, centroids, and map boundaries. | Automated |
| `census_cbp` | 2023 County Business Patterns | U.S. Census Bureau | Establishments, employment, payroll, establishment-size mix, business density, and local industry context. | Automated |
| `census_popest` | Vintage 2025 County Population Estimates | U.S. Census Bureau Population Estimates Program | Resident population denominators for county rates and brief context. | Automated |
| `census_saipe` | 2024 Small Area Income and Poverty Estimates | U.S. Census Bureau Small Area Income and Poverty Estimates Program | Poverty and median household income context. | Automated |
| `census_acs` | 2023 ACS 5-year detailed tables | U.S. Census Bureau | Optional household, education, transportation, internet, rent, income, poverty, and labor-force context. | Optional token |
| `fdic_bankfind` | FDIC BankFind Suite branch locations | Federal Deposit Insurance Corporation | Branch counts and branch-density measures after county matching. | Automated |
| `fdic_sod` | FDIC Summary of Deposits | Federal Deposit Insurance Corporation | Branch deposit context where available from the Summary of Deposits API. | Automated |
| `bls_laus` | BLS Local Area Unemployment Statistics county import | U.S. Bureau of Labor Statistics | Annual unemployment-rate context. | Manual optional |
| `ffiec_cra` | 2024 FFIEC CRA small-business lending aggregate county file | Federal Financial Institutions Examination Council | Public small-business lending originations by county. | Automated, source may block scripted download |
| `sba` | SBA 7(a)/504 lending county aggregate | U.S. Small Business Administration | SBA lending activity by county. | Automated |
| `cdfi` | Certified CDFI county aggregate | Community Development Financial Institutions Fund | Certified CDFI headquarters count by county. | Automated |
| `hud_fmr` | HUD Fair Market Rents / Income Limits county context | U.S. Department of Housing and Urban Development | Optional housing-cost pressure context. | Optional token |

## Automated Default Sources

The default `python -m mainstreet_atlas.cli all` build fetches or reuses cached public files for:

- Census county cartographic boundaries
- Census County Business Patterns
- Census Population Estimates Program county estimates
- Census Small Area Income and Poverty Estimates
- FDIC BankFind branch locations
- FDIC Summary of Deposits
- FFIEC CRA Aggregate Data flat file, parsed from county-level small-business originations when the official zip is reachable
- SBA 7(a)/504 public FOIA current-period files, aggregated to county level
- CDFI Fund certified CDFI list, aggregated to county level with the Census ZCTA-county relationship file

Raw downloads are cached in `data/raw/`. Processed source outputs are written to `data/processed/`. Published public exports are written to `data/public/` and copied into the generated static site under `site/dist/assets/data/`.

## Optional Token Sources

`CENSUS_API_KEY` enables the ACS adapter. The adapter reads Census API metadata before requesting variables so the build is less brittle when variable labels or endpoints change.

Local `.env` files are supported for developer convenience and are ignored by Git. Repository and deployment environments should use GitHub Actions secrets or equivalent secret storage.

`HUD_API_TOKEN` enables the HUD Fair Market Rents API adapter. The adapter fetches state-level FMR data and computes annual two-bedroom FMR as a share of Census SAIPE median household income when both values are present. The default build does not require the token. When HUD data is absent, housing fields remain unavailable and the source manifest records that limitation.

`CRA_YEAR` optionally sets the FFIEC CRA Aggregate Data year. The default is 2024, matching the latest CRA flat-file year currently published by FFIEC. The adapter uses the official aggregate flat-file zip and parses fixed-width table `A1-1` county-total small-business originations. Some local or CI environments may receive HTTP 403 responses from FFIEC's download host; the build records that status as unavailable rather than using unofficial mirrors or fabricated values.

## Manual County CSV Sources

Manual files live in `data/manual/` and are documented in `data/manual/README.md`. They are fallback or override paths for sources that cannot be fetched automatically in a given environment.

Supported manual paths:

- `data/manual/bls_laus_county.csv`
- `data/manual/ffiec_cra_county.csv`
- `data/manual/hud_county.csv`

Manual imports are strict by design:

- Five-digit county FIPS codes are required.
- Unsupported columns are rejected.
- Duplicate county rows are rejected.
- Invalid county FIPS values are rejected.
- Nonnumeric measure values are rejected.
- Row-level sensitive fields, business names, personal names, contact details, addresses, application identifiers, and private records should not be included.

Manual files should already be aggregated to county level before import. Keep source URLs, preprocessing notes, and methodology notes in a pull request or companion documentation rather than embedding them in county CSV rows.

## Generated Public Data Package

Each successful build publishes:

- `data/public/counties.csv`
- `data/public/counties.json`
- `data/public/county-map.geojson`
- `data/public/source_manifest.json`
- `data/public/data_dictionary.csv`
- `data/public/data_dictionary.json`
- `data/public/data_package_manifest.json`

The generated website copies those files into `site/dist/assets/data/` and also creates `site/dist/assets/data/county-search.json` as a compact client-side search index.

County CSV, JSON, search, and generated brief pages cover every county and county-equivalent record. The GeoJSON map payload is intentionally scoped to the contiguous-U.S. homepage choropleth for browser performance and readability.

## Refresh And Review

For a local refresh:

```bash
python -m mainstreet_atlas.cli all --refresh
python -m pytest
python -m ruff check .
```

Before publishing refreshed data:

- Review `data/public/source_manifest.json` for source status, vintage, access method, coverage, and limitations.
- Review `data/public/data_package_manifest.json` for row counts, feature counts, file sizes, and SHA-256 checksums.
- Spot-check the generated Sources page and representative county briefs.
- Confirm missing fields remain visible and no unavailable source has been silently imputed.
- Confirm the public language still frames the atlas as a local-verification and conversation-starting tool.
