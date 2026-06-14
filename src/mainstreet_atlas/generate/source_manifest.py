"""Read and write the machine-readable source manifest."""

from __future__ import annotations

from pathlib import Path

from mainstreet_atlas.fetch.common import read_json, write_json
from mainstreet_atlas.paths import PUBLIC_DATA_DIR
from mainstreet_atlas.schemas import SourceRecord

MANIFEST_PATH = PUBLIC_DATA_DIR / "source_manifest.json"


def read_manifest(path: Path = MANIFEST_PATH) -> list[dict]:
    return read_json(path, [])


def write_manifest(records: list[dict], path: Path = MANIFEST_PATH) -> None:
    validated = [SourceRecord(**record).model_dump() for record in records]
    write_json(path, validated)


def upsert_source(record: dict, path: Path = MANIFEST_PATH) -> None:
    records = read_manifest(path)
    others = [item for item in records if item.get("id") != record.get("id")]
    write_manifest([*others, record], path)
