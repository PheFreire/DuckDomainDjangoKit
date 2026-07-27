import pytest

from dddk import (
    AppError,
    RequestDto,
)


class _CreateUserRequest(RequestDto):
    name: str
    email: str


def test_validate_or_error_returns_instance_for_valid_data():
    request = _CreateUserRequest.validate_or_error(
        {"name": "Alice", "email": "alice@example.com"}
    )
    assert isinstance(request, _CreateUserRequest)
    assert request.name == "Alice"


def test_validate_or_error_raises_app_error_for_invalid_type():
    with pytest.raises(AppError) as exc_info:
        _CreateUserRequest.validate_or_error({"name": "Alice", "email": 123})

    error = exc_info.value
    assert error.code == 422
    assert error.details["provided"] == {"name": "Alice", "email": 123}
    assert len(error.details["error"]) >= 1


def test_validate_or_error_raises_app_error_for_missing_field():
    with pytest.raises(AppError) as exc_info:
        _CreateUserRequest.validate_or_error({"name": "Alice"})
    assert exc_info.value.code == 422


def test_validate_or_error_rejects_unknown_fields():
    with pytest.raises(AppError) as exc_info:
        _CreateUserRequest.validate_or_error(
            {"name": "Alice", "email": "a@b.com", "extra": "nope"}
        )
    assert exc_info.value.code == 422
