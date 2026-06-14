# Attribution And Citation

Main Street Capital Access Atlas combines open-source software, public datasets, and open map tooling. Reusers should cite the project and preserve source attribution for the underlying public data.

## Cite The Project

Use `CITATION.cff` when a platform supports citation files. A plain-language citation can use:

> Main Street Capital Access Atlas contributors. Main Street Capital Access Atlas. Version 0.1.0. Open-source public-data project, 2026.

If you publish analysis based on generated county exports, include the build date, the files used, and any manual sources you added.

## Cite The Underlying Data

The project does not own the underlying public datasets. Review `data/public/source_manifest.json` for dataset name, publisher, access method, source URL, status, coverage, limitations, and last fetched date.

At minimum, cite:

- U.S. Census Bureau sources used for county geometry, County Business Patterns, population estimates, SAIPE, and optional ACS context.
- Federal Deposit Insurance Corporation sources used for BankFind branch records and Summary of Deposits context.
- Any manual BLS, FFIEC CRA, SBA, CDFI, HUD, or local-resource files you add.

Source publishers do not endorse this project or any interpretation of the generated outputs.

## Map Attribution

The generated website uses Leaflet for the interactive map and OpenStreetMap map tiles. The live site includes OpenStreetMap contributor attribution in the map control.

If you reuse screenshots or map views, preserve visible map attribution where practical.

## Generated Exports

The project-generated software and templates are MIT licensed. Public datasets may have their own public-domain status, open-data terms, or source-specific usage guidance. Reusers are responsible for complying with source publisher terms and documenting any transformations they make.

Generated files include checksums and row counts in `data/public/data_package_manifest.json` so downstream users can identify exactly which export they used.
