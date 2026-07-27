from datetime import (
    datetime,
)

from pydantic import (
    Field,
)

from dddk.types.null import (
    Null,
)
from dddk.types.null_or import (
    NullOr,
)
from dddk.types.base_dto import (
    BaseDto,
)


class WhereDto(BaseDto):
    """
    Base Data Transfer Object (DTO) for defining filtering and query conditions
    used in repository or data access operations.

    This class is designed to express "where" clauses in a type-safe,
    declarative way. It ensures that all subclass fields are compatible with
    `NullOr` types, allowing flexible filtering (e.g., optional or ignored
    conditions when the value is `Null`).

    The `validate_null_or_field` validator is automatically applied during
    subclass creation, ensuring that all fields follow the expected `NullOr`
    typing convention for query parameters.

    Example
    -------
        class ResearchWhereDto(WhereDto):
            title: NullOr[str]
            author_id: NullOr[UUID]

        # Example usage:
        filters = ResearchWhereDto(title="Research")
        # Generates query conditions equivalent to WHERE title = 'Research'

    Notes
    -----
    - Fields typed as `NullOr[T]` can represent both an active condition (`T`)
      or an ignored one (`Null`), enabling dynamic query composition.
    - Validation runs at class definition time to guarantee that each field
      supports nullable semantics.
    - `WhereDto` is typically consumed by repository implementations to build
      ORM or SQL-level query filters dynamically.

    Raises
    ------
    TypeError
        If any subclass field does not use a `NullOr` type.
    """

    uuids: NullOr[list[str]] = Field(default=Null)
    uuid: NullOr[str] = Field(default=Null)

    created_at: NullOr[datetime] = Field(default=Null)
    updated_at: NullOr[datetime] = Field(default=Null)
    deleted_at: NullOr[datetime | None] = Field(default=Null)
