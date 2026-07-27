import json

import pytest
from pydantic import (
    Field,
)

from dddk import (
    Null,
    NullOr,
    BaseDto,
    AppError,
)


class _SampleDto(BaseDto):
    name: str
    nickname: NullOr[str] = Field(default=Null)


def test_get_returns_attribute_when_type_matches():
    dto = _SampleDto(name="Alice")
    assert dto.get("name", str) == "Alice"


def test_get_raises_app_error_when_attribute_missing():
    dto = _SampleDto(name="Alice")
    with pytest.raises(AppError) as exc_info:
        dto.get("does_not_exist", str)
    assert exc_info.value.title == "KeyError"
    assert exc_info.value.code == 500


def test_get_raises_app_error_when_type_does_not_match():
    dto = _SampleDto(name="Alice")
    with pytest.raises(AppError) as exc_info:
        dto.get("name", int)
    assert exc_info.value.title == "TypeError"
    assert exc_info.value.code == 500


def test_null_field_serializes_to_json_null():
    dto = _SampleDto(name="Alice")
    payload = json.loads(dto.model_dump_json())
    assert payload["nickname"] is None


def test_present_field_serializes_normally_to_json():
    dto = _SampleDto(name="Alice", nickname="Ali")
    payload = json.loads(dto.model_dump_json())
    assert payload["nickname"] == "Ali"


def test_null_field_is_preserved_as_null_sentinel_in_python():
    dto = _SampleDto(name="Alice")
    assert dto.nickname == Null
