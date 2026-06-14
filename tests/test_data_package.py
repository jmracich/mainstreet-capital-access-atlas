import csv
import hashlib
import json
from pathlib import Path

import pytest

from mainstreet_atlas.generate.data_package import (
    DATA_PACKAGE_MANIFEST,
    PUBLIC_DATA_PACKAGE_FILES,
)


def test_data_package_manifest_matches_generated_files():
    root = Path("data/public")
    manifest_path = root / DATA_PACKAGE_MANIFEST
    if not manifest_path.exists():
        pytest.skip("Generated data package manifest is not present.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest["files"]
    by_name = {Path(record["path"]).name: record for record in files}

    assert set(by_name) == set(PUBLIC_DATA_PACKAGE_FILES)
    assert manifest["generated_at"]

    for file_name in PUBLIC_DATA_PACKAGE_FILES:
        path = root / file_name
        record = by_name[file_name]
        assert path.exists()
        assert record["bytes"] == path.stat().st_size
        assert record["sha256"] == _sha256(path)

    assert by_name["counties.csv"]["row_count"] == _csv_rows(root / "counties.csv")
    assert by_name["data_dictionary.csv"]["row_count"] == _csv_rows(root / "data_dictionary.csv")
    assert by_name["counties.json"]["record_count"] == len(
        json.loads((root / "counties.json").read_text(encoding="utf-8"))
    )
    county_map = json.loads((root / "county-map.geojson").read_text(encoding="utf-8"))
    assert by_name["county-map.geojson"]["feature_count"] == len(county_map["features"])


def test_site_publishes_only_intentional_data_assets():
    root = Path("site/dist/assets/data")
    if not root.exists():
        pytest.skip("Generated site data assets are not present.")

    files = {path.name for path in root.iterdir() if path.is_file()}
    expected = {
        *PUBLIC_DATA_PACKAGE_FILES,
        DATA_PACKAGE_MANIFEST,
        "county-search.json",
    }

    assert files == expected
    assert ".gitkeep" not in files
    assert "counties.geojson" not in files


def test_data_source_documentation_covers_source_manifest():
    manifest_path = Path("data/public/source_manifest.json")
    if not manifest_path.exists():
        pytest.skip("Generated source manifest is not present.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    docs = Path("docs/data_sources.md").read_text(encoding="utf-8")

    missing: list[str] = []
    for record in manifest:
        for value in [record["id"], record["dataset_name"], record["publisher"]]:
            if value not in docs:
                missing.append(value)

    assert missing == []


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_rows(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as file:
        return max(sum(1 for _ in csv.reader(file)) - 1, 0)
