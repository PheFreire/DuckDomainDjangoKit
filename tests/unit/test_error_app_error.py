import pytest

from dddk import (
    AppError,
)


def test_default_code_is_400():
    error = AppError("pointer", "Some Error")
    assert error.code == 400
    assert error.message == ""
    assert error.details == {}


def test_error_property_shape():
    error = AppError(
        "pointer", "Some Error", "Something went wrong", {"key": "value"}, 409
    )
    payload = error.error
    assert payload["title"] == "Some Error"
    assert payload["message"] == "Something went wrong"
    assert payload["details"] == {"key": "value"}
    assert payload["code"] == 409
    assert payload["class_name"] == "pointer"
    assert "caller" in payload and ":" in payload["caller"]


def test_class_pointer_as_none_resolves_to_empty_string():
    error = AppError(None, "Some Error")
    assert error._resolve_pointer() == ""


def test_class_pointer_as_instance_resolves_to_class_name():
    class Foo:
        pass

    error = AppError(Foo(), "Some Error")
    assert error._resolve_pointer() == "Foo"


def test_class_pointer_as_string_is_kept_as_is():
    error = AppError("MyUsecase", "Some Error")
    assert error._resolve_pointer() == "MyUsecase"


def test_str_contains_title_code_and_message():
    error = AppError("pointer", "Some Error", "boom", code=404)
    text = str(error)
    assert "(404)[SOME ERROR]: boom" in text


def test_str_does_not_raise_when_details_are_not_json_serializable():
    class Unserializable:
        pass

    error = AppError(
        "pointer", "Some Error", "boom", {"obj": Unserializable()}
    )
    # `default=str` in json.dumps makes even non-serializable objects work,
    # so this should never hit the except-branch, but must not raise either.
    text = str(error)
    assert "Some Error" in text


def test_is_an_exception_that_can_be_raised_and_caught():
    with pytest.raises(AppError) as exc_info:
        raise AppError("pointer", "Some Error", "boom")
    assert isinstance(exc_info.value, Exception)
