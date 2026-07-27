import pytest

from dddk import (
    AppError,
)
from dddk.envs.adapters.envs_toml import (
    EnvsToml,
)


@pytest.fixture()
def settings_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "settings.toml"
    toml_file.write_text(
        "\n".join(
            [
                "[log]",
                "is_active = false",
                "indent = 2",
                "",
                "[debug]",
                "is_active = true",
                "",
                "[api]",
                'allowed_hosts = ["example.com"]',
            ]
        )
    )
    monkeypatch.setenv("SETTINGS_PATH", str(toml_file))
    monkeypatch.setenv(
        "DATABASE_URL", "postgres://user:pass@localhost:5432/db"
    )
    return toml_file


def test_log_property_reads_toml_section(settings_file):
    envs = EnvsToml()
    log = envs.log
    assert log.is_active is False
    assert log.indent == 2


def test_debug_property_reads_toml_section(settings_file):
    envs = EnvsToml()
    assert envs.debug.is_active is True


def test_api_property_reads_toml_section(settings_file):
    envs = EnvsToml()
    assert envs.api.allowed_hosts == ["example.com"]


def test_database_property_reads_from_env_var_directly(settings_file):
    envs = EnvsToml()
    assert envs.database.url == "postgres://user:pass@localhost:5432/db"


def test_raises_app_error_when_settings_path_env_var_is_missing(monkeypatch):
    monkeypatch.delenv("SETTINGS_PATH", raising=False)
    with pytest.raises(AppError) as exc_info:
        EnvsToml().log
    assert exc_info.value.title == "Env Key Error"
    assert exc_info.value.code == 500


def test_raises_app_error_when_toml_section_is_missing(tmp_path, monkeypatch):
    toml_file = tmp_path / "settings.toml"
    toml_file.write_text("[log]\nis_active = true\n")
    monkeypatch.setenv("SETTINGS_PATH", str(toml_file))

    with pytest.raises(AppError) as exc_info:
        EnvsToml().debug
    assert exc_info.value.title == "Missing TOML Section"
