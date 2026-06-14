# Release Checklist

Use this checklist before announcing a public release or refreshing the live site.

## Build

- Review `docs/generated_artifacts.md` so source changes and generated-output changes are evaluated separately.
- Run `python -m mainstreet_atlas.cli all`.
- Confirm `site/dist/index.html` exists.
- Confirm `site/dist/404.html` and `site/dist/.nojekyll` exist for GitHub Pages hosting.
- Confirm `site/dist/counties/` contains generated county pages.
- Confirm `data/public/source_manifest.json` lists every automated, optional, and manual source.
- For public deployment, set or confirm `SITE_URL` so `site/dist/sitemap.xml` is generated with absolute URLs.

## Verification

- Run `python -m pytest`.
- Run `python -m ruff check .`.
- Open the local site and check the browser console for errors.
- Spot-check the homepage, Illinois spotlight, methodology, limitations, sources, contribute page, and at least one county brief.
- Confirm `site/dist/robots.txt` exists and points to `sitemap.xml` when `SITE_URL` is configured.

## Data Review

- Confirm no official data was fabricated.
- Confirm missing fields are visible on county pages.
- Confirm source vintages and manual sources are represented honestly.
- Confirm generated source paths are repository-relative.

## Language Review

- Confirm the site says the project is independent and public-data-based.
- Confirm the site does not imply sponsorship, endorsement, partnership, or affiliation.
- Confirm the site does not frame outputs as credit decisions, underwriting guidance, or definitive rankings of community worth.
- Confirm limitations remain prominent.

## Deployment

- Use the GitHub Pages workflow for deployment.
- Use the refresh workflow for scheduled or manual data refreshes.
- Review generated data changes before announcing a refreshed release.
- Update `CHANGELOG.md` with verified commands, data/source status, and any external release gates.
