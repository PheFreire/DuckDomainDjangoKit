import pytest

from dddk import (
    AppError,
)
from dddk.envs.models import (
    ApiSettingsDto,
    LogSettingsDto,
    DebugSettingsDto,
    DatabaseSettingsDto,
)


def test_api_settings_defaults():
    settings = ApiSettingsDto()
    assert settings.allowed_hosts == []
    assert settings.cors_allowed_hosts == []


def test_debug_settings_defaults():
    settings = DebugSettingsDto()
    assert settings.is_active is False
    assert settings.labels == []
    assert settings.levels == []


def test_log_settings_defaults():
    settings = LogSettingsDto()
    assert settings.is_active is True
    assert settings.indent == 3
    assert settings.labels == []
    assert settings.levels == []


@pytest.mark.parametrize(
    "url",
    [
        "postgres://user:pass@localhost:5432/db",
        "postgresql://user:pass@localhost:5432/db",
        "sqlite:///db.sqlite3",
        "mysql://user@localhost/db",
    ],
)
def test_database_url_accepts_valid_formats(url):
    assert DatabaseSettingsDto(url=url).url == url


def test_database_url_rejects_invalid_format():
    with pytest.raises(AppError) as exc_info:
        DatabaseSettingsDto(url="not-a-database-url")
    assert exc_info.value.code == 400
    assert exc_info.value.title == "Invalid DATABASE_URL format error"
