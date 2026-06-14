"""Filesystem paths used by the build pipeline."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
ROOT = PACKAGE_DIR.parents[1]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MANUAL_DIR = DATA_DIR / "manual"
PROCESSED_DIR = DATA_DIR / "processed"
PUBLIC_DATA_DIR = DATA_DIR / "public"

SITE_DIR = ROOT / "site"
TEMPLATE_DIR = SITE_DIR / "templates"
STATIC_DIR = SITE_DIR / "static"
DIST_DIR = SITE_DIR / "dist"

DOCS_DIR = ROOT / "docs"


def ensure_directories() -> None:
    for path in [
        RAW_DIR,
        MANUAL_DIR,
        PROCESSED_DIR,
        PUBLIC_DATA_DIR,
        TEMPLATE_DIR,
        STATIC_DIR,
        DIST_DIR,
        DOCS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
