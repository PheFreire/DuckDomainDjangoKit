import pytest

from dddk import (
    AppError,
)
from dddk.utils.parser import (
    Parser,
)


def test_toml_load_returns_parsed_content(tmp_path):
    toml_file = tmp_path / "settings.toml"
    toml_file.write_text('[api]\nallowed_hosts = ["localhost"]\n')

    result = Parser().toml_load(str(toml_file))

    assert result == {"api": {"allowed_hosts": ["localhost"]}}


def test_toml_load_raises_app_error_for_missing_file():
    with pytest.raises(AppError) as exc_info:
        Parser().toml_load("/path/does/not/exist.toml")

    error = exc_info.value
    assert error.title == "TomlFileLoadError"
    assert error.code == 500
    assert error.details["invalid_path"] == "/path/does/not/exist.toml"


def test_toml_load_raises_app_error_for_invalid_toml(tmp_path):
    toml_file = tmp_path / "broken.toml"
    toml_file.write_text("this is not valid toml [[[")

    with pytest.raises(AppError) as exc_info:
        Parser().toml_load(str(toml_file))

    assert exc_info.value.title == "TomlFileLoadError"
