from dddk.types.null import (
    Null,
    _TypeNull,
)


def test_null_is_falsy():
    assert bool(Null) is False


def test_null_str_and_repr():
    assert str(Null) == "null"
    assert repr(Null) == "Null"


def test_null_equals_another_type_null_instance():
    assert Null == _TypeNull()


def test_null_does_not_equal_none():
    assert (Null == None) is False  # noqa: E711


def test_null_does_not_equal_arbitrary_value():
    assert (Null == "null") is False
    assert (Null == 0) is False
