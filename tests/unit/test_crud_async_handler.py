from dddk import (
    AppError,
)
from dddk.crud.tools.async_handler import (
    AsyncHandler,
)


def test_get_chunks_splits_evenly_when_divisible():
    handler = AsyncHandler(list(range(10)), "Item")
    chunks = list(handler.get_chunks(5))
    assert [len(c) for c in chunks] == [2, 2, 2, 2, 2]
    assert sum(chunks, []) == list(range(10))


def test_get_chunks_distributes_remainder_to_first_chunks():
    handler = AsyncHandler(list(range(7)), "Item")
    chunks = list(handler.get_chunks(3))
    assert [len(c) for c in chunks] == [3, 2, 2]
    assert sum(chunks, []) == list(range(7))


def test_get_chunks_never_exceeds_total_items():
    handler = AsyncHandler(list(range(2)), "Item")
    chunks = list(handler.get_chunks(10))
    assert sum(len(c) for c in chunks) == 2


def test_parallel_map_preserves_all_items_and_order_of_chunks():
    handler = AsyncHandler(list(range(20)), "Item")
    result = handler.parallel_map(
        lambda chunk: [x * 2 for x in chunk], divisions=4
    )
    assert sorted(result) == [x * 2 for x in range(20)]


def test_parallel_map_returns_empty_list_for_empty_data():
    handler = AsyncHandler([], "Item")
    assert handler.parallel_map(lambda chunk: chunk) == []


def test_parallel_map_returns_app_error_for_non_callable():
    handler = AsyncHandler([1, 2], "Item")
    result = handler.parallel_map("not-callable")  # type: ignore[arg-type]
    assert isinstance(result, AppError)
    assert result.title == "Invalid Function Argument"
    assert result.code == 400


def test_parallel_map_returns_app_error_when_chunk_processing_fails():
    def boom(chunk):
        raise ValueError("kaboom")

    handler = AsyncHandler([1, 2, 3], "Item")
    result = handler.parallel_map(boom, divisions=1)
    assert isinstance(result, AppError)
    assert result.title == "Threaded Execution Failed"
    assert result.details["exception_type"] == "ValueError"


def test_dunder_helpers():
    handler = AsyncHandler([1, 2, 3], "Item")
    assert len(handler) == 3
    assert handler[0] == 1
    assert list(iter(handler)) == [1, 2, 3]
    assert bool(handler) is True
    assert bool(AsyncHandler([], "Item")) is False
    assert "Item" in repr(handler)
