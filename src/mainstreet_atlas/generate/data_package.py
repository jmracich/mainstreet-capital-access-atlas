"""Generate a manifest for public data package artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from mainstreet_atlas.fetch.common import utc_now, write_json
from mainstreet_atlas.paths import PUBLIC_DATA_DIR

PUBLIC_DATA_PACKAGE_FILES = [
    "counties.csv",
    "counties.json",
    "county-map.geojson",
    "source_manifest.json",
    "data_dictionary.csv",
    "data_dictionary.json",
]

DATA_PACKAGE_MANIFEST = "data_package_manifest.json"


def write_data_package_manifest(
    directory: Path = PUBLIC_DATA_DIR,
    file_names: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Write checksums and record counts for intended public data files."""

    names = file_names or PUBLIC_DATA_PACKAGE_FILES
    records = [_file_record(directory / name) for name in names]
    payload = {
        "generated_at": utc_now(),
        "files": records,
    }
    write_json(directory / DATA_PACKAGE_MANIFEST, payload)
    return records


def _file_record(path: Path) -> dict[str, Any]:
    if not path.exists():
        msg = f"Public data package file is missing: {path}"
        raise FileNotFoundError(msg)

    record: dict[str, Any] = {
        "path": f"data/public/{path.name}",
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }
    record.update(_content_counts(path))
    return record


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _content_counts(path: Path) -> dict[str, int]:
    if path.suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as file:
            row_count = sum(1 for _ in csv.reader(file))
        return {"row_count": max(row_count - 1, 0)}

    if path.suffix == ".json" or path.suffix == ".geojson":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return {"record_count": len(payload)}
        if isinstance(payload, dict) and isinstance(payload.get("features"), list):
            return {"feature_count": len(payload["features"])}
        if isinstance(payload, dict):
            return {"top_level_keys": len(payload)}

    return {}
