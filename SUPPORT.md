# Support

Main Street Capital Access Atlas is an open-source civic-data project. It is intended to help community partners ask better questions with public data, not to provide individualized financial, legal, policy, underwriting, or investment advice.

## Where To Ask

- Data issue: use the data issue template with county FIPS, observed value, expected value, public source URL, and source vintage.
- Methodology feedback: use the methodology feedback template and describe the proposed calculation or language change plus risks.
- Source request: use the source request template and include publisher, access method, useful fields, coverage, and limitations.
- State spotlight: use the state spotlight template with a balanced set of counties and local context to verify.
- Accessibility issue: use the accessibility template with the page or file, accessibility area, observed behavior, expected behavior, and relevant environment.
- Security or sensitive data concern: follow `SECURITY.md` and do not post sensitive details publicly.

## What Maintainers Can Help With

- Reproducible pipeline failures.
- Data-source availability, vintage, or documentation questions.
- Manual import format questions.
- Accessibility or static-site issues.
- Careful wording that improves transparency and avoids overclaiming.

## What Maintainers Cannot Validate

- Whether a business, borrower, institution, or county should receive financing or investment.
- Whether any place is definitively high need or low need.
- Private, confidential, proprietary, or row-level records.
- Local facts that require resident, business-owner, or community-partner verification.

## Before Opening An Issue

1. Check `README.md`, `docs/methodology.md`, `docs/limitations.md`, `docs/data_sources.md`, and `docs/accessibility.md`.
2. Run `python -m pytest` and `python -m ruff check .` if you are reporting a code change or local build issue.
3. Include the generated source status from `data/public/source_manifest.json` when reporting data availability issues.
4. Avoid attaching private or sensitive files.
