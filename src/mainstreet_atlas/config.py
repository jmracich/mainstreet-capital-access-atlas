"""Runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    acs_year: int = 2023
    cbp_year: int = 2023
    popest_year: int = 2025
    saipe_year: int = 2024
    geography_year: int = 2023
    cra_year: int = 2024
    census_api_key: str | None = None
    hud_api_token: str | None = None
    site_url: str | None = None
    request_timeout_seconds: int = 45
    user_agent: str = (
        "MainStreetCapitalAccessAtlas/0.1 "
        "(open-source civic public-data project; contact: repository maintainers)"
    )


def get_settings() -> Settings:
    return Settings(
        census_api_key=_env("CENSUS_API_KEY"),
        hud_api_token=_env("HUD_API_TOKEN"),
        site_url=_clean_site_url(_env("SITE_URL")),
        cra_year=_env_int("CRA_YEAR", default=Settings.cra_year),
    )


def _env(name: str) -> str | None:
    return os.getenv(name) or _local_env().get(name) or None


def _env_int(name: str, *, default: int) -> int:
    value = _env(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@lru_cache
def _local_env() -> dict[str, str]:
    path = ROOT / ".env"
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def _clean_site_url(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    return text.rstrip("/") + "/"
