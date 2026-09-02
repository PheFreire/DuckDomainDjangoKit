import pytest

from dddk import (
    AppError,
)
from dddk.envs.adapters.envs_toml import (
    EnvsToml,
)


def test_database_property_reads_from_env_var(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL", "postgres://user:pass@localhost:5432/db"
    )
    envs = EnvsToml()
    assert envs.database.url == "postgres://user:pass@localhost:5432/db"


def test_raises_app_error_when_database_url_env_var_is_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(AppError) as exc_info:
        EnvsToml().database
    assert exc_info.value.title == "Env Key Error"
    assert exc_info.value.code == 500
