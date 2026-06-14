"""Shared fetch utilities."""

from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from requests import RequestException

from mainstreet_atlas.config import Settings
from mainstreet_atlas.paths import ROOT

LOGGER = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def request_session(settings: Settings) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": settings.user_agent})
    return session


def download_file(
    url: str,
    destination: Path,
    settings: Settings,
    refresh: bool = False,
    attempts: int = 3,
) -> bool:
    if destination.exists() and not refresh:
        LOGGER.info("Using cached file %s", destination)
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    session = request_session(settings)
    last_error: RequestException | None = None
    for attempt in range(1, attempts + 1):
        try:
            LOGGER.info("Downloading %s", url)
            temp_destination = destination.with_suffix(destination.suffix + ".tmp")
            with session.get(url, stream=True, timeout=settings.request_timeout_seconds) as response:
                response.raise_for_status()
                with temp_destination.open("wb") as file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            file.write(chunk)
            temp_destination.replace(destination)
            return True
        except RequestException as exc:
            last_error = exc
            LOGGER.warning("Download attempt %s/%s failed for %s: %s", attempt, attempts, url, exc)
            if attempt < attempts:
                time.sleep(2 * attempt)
    if last_error:
        raise last_error
    return False


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_county_name(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.upper().strip()
    replacements = {
        " COUNTY": "",
        " PARISH": "",
        " BOROUGH": "",
        " CENSUS AREA": "",
        " MUNICIPALITY": "",
        " CITY AND BOROUGH": "",
        " CITY": "",
        ".": "",
        "'": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def source_record(
    *,
    source_id: str,
    dataset_name: str,
    publisher: str,
    access_method: str,
    status: str,
    coverage: str,
    known_limitations: str,
    url: str | None = None,
    local_path: Path | None = None,
    fetched: bool = False,
) -> dict[str, str | None]:
    return {
        "id": source_id,
        "dataset_name": dataset_name,
        "publisher": publisher,
        "access_method": access_method,
        "url": url,
        "status": status,
        "last_fetched": utc_now() if fetched else None,
        "coverage": coverage,
        "known_limitations": known_limitations,
        "local_path": _public_path(local_path),
    }


def _public_path(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()
