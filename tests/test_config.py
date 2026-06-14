from mainstreet_atlas import config


def test_local_env_file_is_read_without_overriding_process_env(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "CENSUS_API_KEY=from_file\nHUD_API_TOKEN='hud_file'\nSITE_URL=\"https://example.org/site\"\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(config, "ROOT", tmp_path)
    config._local_env.cache_clear()
    monkeypatch.setenv("CENSUS_API_KEY", "from_process")

    settings = config.get_settings()

    assert settings.census_api_key == "from_process"
    assert settings.hud_api_token == "hud_file"
    assert settings.site_url == "https://example.org/site/"
