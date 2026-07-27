from __future__ import (
    annotations,
)

from typing import (
    Generic,
    TypeVar,
)
from dataclasses import (
    field,
    dataclass,
)

from dddk.types.base_dto import (
    BaseDto,
)

DTO = TypeVar("DTO", bound=BaseDto)


@dataclass(frozen=True)
class RelationLoaderResult(Generic[DTO]):
    """
    Wrapper returned by ``RelationLoader.load()``.

    Holds the same list of DTOs that was passed in, mutated in-place with
    their resolved relations.  The wrapper exists so callers can chain off
    the result (e.g. ``.items``) without depending on the raw list type.

    Attributes:
        items: The enriched DTO list.  Same object references as the input —
            mutations applied by the loader are visible here and on the
            original list.
    """

    items: list[DTO] = field(default_factory=list)
