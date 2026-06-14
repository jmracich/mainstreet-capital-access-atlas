# Governance

Main Street Capital Access Atlas is maintained as an independent open-source civic-data project. Governance decisions should protect public trust, source transparency, careful language, and the project's usefulness to local partners.

## Decision Principles

Project decisions should prioritize:

- Public benefit and practical usefulness for community partners.
- Source transparency, reproducibility, and clear missing-data handling.
- Careful language that avoids overclaiming, stigmatizing places, or implying deterministic conclusions.
- Static, free-to-host architecture with no default secrets, accounts, paid APIs, or private data.
- Accessibility, documentation quality, and long-term maintainability.
- Independence from any institution, funder, data publisher, or prospective user of the analysis.

## Maintainer Responsibilities

Maintainers should:

- Review source, methodology, template, and workflow changes before generated artifacts.
- Require tests for scoring, source handling, generated public copy, accessibility, or workflow changes when practical.
- Keep the default build runnable without optional credentials or manual files.
- Preserve public source provenance in `data/public/source_manifest.json`.
- Keep limitations prominent on the website and in generated briefs.
- Reject contributions that add private, sensitive, proprietary, or row-level records.

## Methodology Changes

Changes to scoring, weights, normalization, missing-data handling, field definitions, data-quality grades, or public labels require extra care.

Before accepting a methodology change:

- Explain the current behavior and proposed behavior.
- Describe which counties, source fields, or components may be affected.
- Add or update tests for directionality, score ranges, missing-data behavior, and public language.
- Update `docs/methodology.md`, `site/templates/methodology.html`, and the data dictionary when relevant.
- Consider whether the change could be misread as a definitive ranking, eligibility tool, or directive for action.

## Source Changes

New sources or source-adapter changes should:

- Use only public data that can be redistributed or referenced in an open-source project.
- Document publisher, access method, coverage, known limitations, source URL, and vintage.
- Avoid private or row-level records.
- Prefer county-level aggregates for the MVP.
- Continue the build gracefully when optional sources are unavailable.
- Add manual import documentation when automation is not reliable.

## Release Process

Before a public release or data refresh:

1. Run `python -m mainstreet_atlas.cli all`.
2. Run `python -m pytest`.
3. Run `python -m ruff check .`.
4. Review `docs/release_checklist.md`.
5. Review `data/public/data_package_manifest.json` and `data/public/source_manifest.json`.
6. Spot-check representative generated pages, including the homepage, Sources, Methodology, Limitations, Illinois, and county briefs.
7. Confirm `site/dist` remains static and GitHub Pages compatible.

## Disagreement Resolution

When contributors disagree, prefer the option that is more transparent, easier to verify, less likely to be misread, and more cautious about public-data limitations. If a change could materially affect interpretation, open a methodology issue and wait for review before merging.

## Independence

This project should not imply sponsorship, endorsement, partnership, or affiliation with any financial institution, government agency, data publisher, or local organization. External users may reuse the project, but their use does not make them project sponsors or maintainers.
