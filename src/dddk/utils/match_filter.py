from typing import (
    Any,
)


def match_any_filter(filters: list[dict], value: dict) -> bool:
    return any(all(value.get(k) == v for k, v in f.items()) for f in filters)


def unmatch_any_filter(
    filters: list[dict[str, Any]], value: dict[str, Any]
) -> bool:
    return all(
        not all(value.get(k) == v for k, v in f.items()) for f in filters
    )
