# Generated Artifacts

This project separates source files from reproducible generated outputs. Review source, templates, tests, and documentation first; regenerate artifacts from those inputs before release.

## Source Of Truth

Source-controlled inputs include:

- Python package code in `src/mainstreet_atlas/`
- Static templates and hand-authored assets in `site/templates/` and `site/static/`
- Tests in `tests/`
- Documentation in `README.md`, `docs/`, and repository policy files
- Manual import instructions and optional manual CSV inputs in `data/manual/`
- GitHub Actions workflows and issue templates in `.github/`

## Generated Directories

These directories are generated or cached by the pipeline:

| Path | Purpose | Commit guidance |
| --- | --- | --- |
| `data/raw/` | Cached downloaded source files. | Do not review as source; refresh through the pipeline. |
| `data/processed/` | Intermediate normalized source tables. | Do not hand-edit. |
| `data/public/` | Published public data package, dictionary, source manifest, and checksums. | Review summaries, manifests, and diffs when refresh workflows publish updates. |
| `site/dist/` | Deployable static GitHub Pages site. | Regenerate from templates and public data; do not hand-edit. |

The `.gitignore` keeps these generated directories out of ordinary local commits. The refresh workflow may force-add `data/public/` and `site/dist/` when publishing refreshed outputs. `.gitattributes` marks generated directories as generated for GitHub diff readability.

## Regenerate

```bash
python -m mainstreet_atlas.cli all
python -m pytest
python -m ruff check .
```

Use `python -m mainstreet_atlas.cli clean` to remove generated raw, processed, public, and site files before a clean rebuild.

## Review Checklist

When generated files change:

- Confirm `data/public/data_package_manifest.json` has expected row counts, feature counts, file sizes, and SHA-256 checksums.
- Confirm `data/public/source_manifest.json` records source status, coverage, limitations, access method, and vintage.
- Confirm `site/dist/index.html`, `site/dist/404.html`, `site/dist/.nojekyll`, and representative county pages exist.
- Confirm missing optional or manual data is still visible and not silently imputed.
- Confirm generated public copy still avoids prohibited or overclaiming language.

When source files change:

- Prefer reviewing code, templates, and tests before generated diffs.
- Regenerate outputs after source or template changes.
- Do not patch generated HTML, CSV, JSON, or GeoJSON directly unless documenting an emergency remediation.
