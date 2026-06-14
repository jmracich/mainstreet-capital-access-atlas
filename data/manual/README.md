# Manual Data Import Fallbacks

The default pipeline never fabricates official data. These files are fallback or override paths for sources that cannot be fetched automatically in a given environment. When a fallback is needed, add a county-level CSV here and rerun:

```bash
make fetch
make build
make site
```

Every file should use five-digit county FIPS codes. Manual imports are intentionally strict:

- Use only the listed columns for each file.
- Do not include business names, personal names, contact details, addresses, application identifiers, or other row-level sensitive fields.
- Do not include duplicate county FIPS rows.
- Keep source URLs, methodology notes, and preprocessing notes in the pull request or a companion README, not in the county CSV.
- Numeric fields must contain numbers or blank values.

## BLS LAUS

Path: `data/manual/bls_laus_county.csv`

Required columns:

```csv
fips,unemployment_pct,labor_force,employed,unemployed,unemployment_year
17031,5.1,2600000,2467400,132600,2024
```

Only `fips` and `unemployment_pct` are required. The other columns are recommended for transparency and source notes. Use official county-level Local Area Unemployment Statistics annual averages.

## FFIEC CRA

Path: `data/manual/ffiec_cra_county.csv`

The default pipeline attempts to fetch and parse the official FFIEC Aggregate Data flat-file zip automatically. Use this fallback only when the FFIEC download host blocks scripted access or when a reviewed county aggregate is needed for a controlled rebuild.

Required columns:

```csv
fips,cra_small_business_loans,cra_small_business_amount
17031,12345,678900000
```

Only `fips` and `cra_small_business_loans` are required. `cra_small_business_amount` is optional for public context.

## SBA

Path: `data/manual/sba_county.csv`

The default pipeline attempts to fetch and aggregate SBA Open Data files automatically. Use this fallback only when the public source cannot be reached or when a contributor needs a reviewed county aggregate for a controlled rebuild.

Required columns:

```csv
fips,sba_loan_count,sba_loan_amount
17031,321,45600000
```

Only `fips` and `sba_loan_count` are required. `sba_loan_amount` is optional for public context.

## CDFI

Path: `data/manual/cdfi_county.csv`

The default pipeline attempts to fetch the current certified CDFI list and aggregate it by county automatically. Use this fallback only when the public workbook or Census ZIP relationship file cannot be reached.

Required columns:

```csv
fips,cdfi_count
17031,18
```

Use this for a county-level count or presence signal from a public certified CDFI list after geocoding/aggregation.

## HUD

Path: `data/manual/hud_county.csv`

Suggested columns:

```csv
fips,two_bedroom_fmr,fmr_to_income_pct
17031,1650,32.4
```

HUD API access may require `HUD_API_TOKEN`. The default build marks HUD unavailable when this file is absent.
