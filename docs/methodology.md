# Methodology

The Small Business Support Priority Signal is a 0-100 public-data signal designed to help local partners decide where additional verification, listening, and support mapping may be useful.

It is not a credit model, underwriting score, or definitive need index.

## Components

- 20% small-business importance signal, including establishment density, employment density, establishment scale, and small-establishment share when available
- 20% capital-access visibility gap
- 20% community economic stress
- 15% housing/cost pressure
- 15% local support ecosystem gap
- 10% data-quality gap / verification need

Each component is built from available county-level indicators. Missing components are excluded from the weighted average, and the site displays source coverage and a data quality grade.

The default build uses Census Population Estimates Program county population as the denominator for per-resident rates. ACS population is used only as a fallback when ACS is configured and the population-estimates file is unavailable.

The default build also uses Census Small Area Income and Poverty Estimates (SAIPE) for county poverty and median household income when ACS is not configured. SAIPE is model-based and useful for economic context; the site still treats it as a signal to verify locally.

## Normalization

Indicators are converted to 0-100 winsorized percentile scores. Winsorization clips extreme values at the 5th and 95th percentiles before ranking so one outlier does not dominate the signal.

Directionality is explicit. For example, higher poverty or rent burden increases a local verification priority signal, while lower branch density increases a capital-access visibility gap signal.

## Missing Data

Missing official data is not imputed. If a required source is unavailable, the score uses available components and the page displays missingness.
