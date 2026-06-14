"""Command-line interface for the public-data pipeline."""

from __future__ import annotations

import argparse
import logging
import shutil

from mainstreet_atlas.config import get_settings
from mainstreet_atlas.fetch import (
    bls_laus,
    cdfi,
    census_acs,
    census_cbp,
    census_popest,
    census_saipe,
    fdic,
    ffiec_cra,
    geography,
    hud,
    sba,
)
from mainstreet_atlas.generate.site import generate_site
from mainstreet_atlas.logging_utils import configure_logging
from mainstreet_atlas.paths import (
    DIST_DIR,
    PROCESSED_DIR,
    PUBLIC_DATA_DIR,
    RAW_DIR,
    ensure_directories,
)
from mainstreet_atlas.transform.join import build_county_dataset

LOGGER = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mainstreet-atlas",
        description="Build the Main Street Capital Access Atlas static site.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch public data and manual imports.")
    fetch_parser.add_argument("--refresh", action="store_true", help="Re-download cached files.")

    subparsers.add_parser("build", help="Build processed county indicators.")
    subparsers.add_parser("generate-site", help="Generate the static website.")
    all_parser = subparsers.add_parser("all", help="Fetch, build, and generate the static website.")
    all_parser.add_argument("--refresh", action="store_true", help="Re-download cached files.")
    subparsers.add_parser("clean", help="Remove generated raw, processed, public, and site files.")

    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    ensure_directories()
    settings = get_settings()

    if args.command == "fetch":
        fetch_all(settings, refresh=args.refresh)
    elif args.command == "build":
        build_county_dataset()
    elif args.command == "generate-site":
        generate_site()
    elif args.command == "all":
        fetch_all(settings, refresh=args.refresh)
        build_county_dataset()
        generate_site()
    elif args.command == "clean":
        clean_generated()
    else:
        parser.error(f"Unknown command {args.command}")
    return 0


def fetch_all(settings, refresh: bool = False) -> None:
    LOGGER.info("Fetching county geography")
    geography.fetch(settings, refresh=refresh)
    LOGGER.info("Fetching County Business Patterns")
    census_cbp.fetch(settings, refresh=refresh)
    LOGGER.info("Fetching Census county population estimates")
    census_popest.fetch(settings, refresh=refresh)
    LOGGER.info("Fetching Census SAIPE income and poverty estimates")
    census_saipe.fetch(settings, refresh=refresh)
    LOGGER.info("Fetching optional ACS data")
    census_acs.fetch(settings, refresh=refresh)
    LOGGER.info("Fetching FDIC branch data")
    fdic.fetch(settings, refresh=refresh)
    LOGGER.info("Checking manual BLS LAUS import")
    bls_laus.fetch(refresh=refresh)
    LOGGER.info("Fetching FFIEC CRA aggregate data")
    ffiec_cra.fetch(settings, refresh=refresh)
    LOGGER.info("Fetching SBA lending data")
    sba.fetch(settings, refresh=refresh)
    LOGGER.info("Fetching certified CDFI data")
    cdfi.fetch(settings, refresh=refresh)
    LOGGER.info("Checking optional HUD import")
    hud.fetch(settings, refresh=refresh)


def clean_generated() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, PUBLIC_DATA_DIR, DIST_DIR]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Cleaned generated files")


if __name__ == "__main__":
    raise SystemExit(main())
