import pytest

from dddk import (
    Null,
    NullOr,
    BaseDto,
    AppError,
    WhereDto,
)
from dddk.crud.tools.query_response import (
    QueryResponse,
)


class _ItemDto(BaseDto):
    uuid: str
    name: str


class _ItemWhereDto(WhereDto):
    name: NullOr[str] = Null


def _items():
    return [_ItemDto(uuid="1", name="a"), _ItemDto(uuid="2", name="b")]


def test_all_returns_the_full_list():
    qr = QueryResponse(_items(), "Item")
    assert qr.all == _items()


def test_first_returns_first_item_or_none():
    assert QueryResponse(_items(), "Item").first.uuid == "1"
    assert QueryResponse([], "Item").first is None


def test_first_or_error_returns_first_item_when_present():
    assert QueryResponse(_items(), "Item").first_or_error().uuid == "1"


def test_first_or_error_raises_404_when_empty():
    with pytest.raises(AppError) as exc_info:
        QueryResponse([], "Item").first_or_error()
    assert exc_info.value.code == 404
    assert "Item" in exc_info.value.title


def test_all_or_error_raises_404_when_empty():
    with pytest.raises(AppError) as exc_info:
        QueryResponse([], "Item").all_or_error()
    assert exc_info.value.code == 404


def test_all_or_error_returns_list_when_present():
    assert QueryResponse(_items(), "Item").all_or_error() == _items()


def test_empty_or_error_raises_409_when_not_empty():
    with pytest.raises(AppError) as exc_info:
        QueryResponse(_items(), "Item").empty_or_error()
    assert exc_info.value.code == 409


def test_empty_or_error_returns_none_when_empty():
    assert QueryResponse([], "Item").empty_or_error() is None


def test_exists_or_error_raises_404_when_empty():
    with pytest.raises(AppError) as exc_info:
        QueryResponse([], "Item").exists_or_error()
    assert exc_info.value.code == 404


def test_exists_or_error_returns_none_when_present():
    assert QueryResponse(_items(), "Item").exists_or_error() is None


def test_to_dict_serializes_dtos_and_filters():
    where = _ItemWhereDto(name="a")
    qr = QueryResponse(_items(), "Item", where)
    payload = qr.to_dict()
    assert payload["count"] == 2
    assert payload["filters"]["name"] == "a"
    assert payload["data"][0]["uuid"] == "1"


def test_to_dict_filters_is_empty_dict_when_where_is_none():
    payload = QueryResponse(_items(), "Item").to_dict()
    assert payload["filters"] == {}


def test_to_dict_formats_non_dto_items():
    payload = QueryResponse([1, 2], "Item").to_dict()
    assert payload["data"] == ["1", "2"]


def test_parallel_map_transforms_items():
    def double_names(chunk: list[_ItemDto]) -> list[str]:
        return [item.name * 2 for item in chunk]

    result = QueryResponse(_items(), "Item").parallel_map(double_names)
    assert isinstance(result, QueryResponse)
    assert sorted(result.all) == ["aa", "bb"]


def test_parallel_map_raises_app_error_for_invalid_func():
    with pytest.raises(AppError):
        QueryResponse(_items(), "Item").parallel_map(func="not-callable")  # type: ignore[arg-type]


def test_len_iter_getitem_bool_repr():
    qr = QueryResponse(_items(), "Item")
    assert len(qr) == 2
    assert list(iter(qr)) == _items()
    assert qr[0].uuid == "1"
    assert bool(qr) is True
    assert bool(QueryResponse([], "Item")) is False
    assert "Item" in repr(qr)
    assert "2" in repr(qr)
