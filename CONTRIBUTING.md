# Contributing

Main Street Capital Access Atlas is built for public-interest use. Contributions are welcome when they improve data quality, transparency, accessibility, documentation, or the care with which the project communicates uncertainty.

## Ways to Help

- Report data issues with the source, county FIPS, expected value, observed value, and a link to the public source.
- Add a documented manual data file for CRA, SBA, CDFI, local resource, or state spotlight coverage.
- Improve fetch adapters for official public datasets that do not require paid services or secrets by default.
- Strengthen tests for scoring directionality, missing data, accessibility, and language safety.
- Improve county brief copy so it remains careful, humble, and useful to local partners.

## Opening Issues

Use the GitHub issue templates so reports include enough evidence to act on:

- Data issues should include county FIPS, observed value, expected value, public source URL, and source vintage.
- Data source requests should identify publisher, access method, useful fields, coverage, and known limitations.
- Methodology feedback should describe the proposed calculation or language change plus risks and safeguards.
- State spotlight suggestions should include a balanced set of counties and local context to verify.
- Accessibility issues should identify the page or file, accessibility area, observed behavior, expected behavior, and relevant browser/device or assistive technology context.

For general support routing, see [SUPPORT.md](SUPPORT.md). For suspected vulnerabilities, exposed credentials, or accidental sensitive-data disclosure, follow [SECURITY.md](SECURITY.md) and do not post sensitive details publicly.

For project decision principles, methodology-change expectations, source acceptance standards, release process, and independence rules, see [GOVERNANCE.md](GOVERNANCE.md).

## Development

```bash
make install
make all
make test
make lint
```

Generated data and site output are intentionally reproducible. If you change source code or templates, regenerate the site before opening a pull request.

See [docs/generated_artifacts.md](docs/generated_artifacts.md) for which directories are generated, when generated outputs may be force-added by workflows, and how to review regenerated data/site files.

## Standards

- Do not add private, sensitive, or personally identifiable data.
- Do not fabricate official data.
- Do not frame outputs as credit decisions, underwriting tools, or definitive rankings of community worth.
- Cite official public sources wherever practical.
- Keep the default build free to run and free to host.
- Run the public-output quality tests before proposing public copy or template changes.
