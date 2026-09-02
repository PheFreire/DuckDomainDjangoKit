import pytest

from dddk import (
    AppError,
)
from dddk.envs.models import (
    DatabaseSettingsDto,
)


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
