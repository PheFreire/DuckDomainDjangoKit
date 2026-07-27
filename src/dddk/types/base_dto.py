from pydantic import (
    BaseModel,
    ConfigDict,
    field_serializer,
)

from dddk.types.null import (
    Null,
)
from dddk.error.app_error import (
    AppError,
)


class BaseDto(BaseModel):
    """
    Base class for all domain Data Transfer Objects (DTOs).

    This class extends Pydantic's `BaseModel` to provide consistent behavior
    across all DTOs within the domain layer. It introduces custom serialization
    rules and relaxed type constraints to support domain-specific abstractions
    such as `Null` and `NullOr[T]`.

    Features
    --------
    - Allows arbitrary types (`arbitrary_types_allowed=True`) to support custom
      domain classes and framework-specific objects.
    - Automatically serializes the custom `Null` sentinel to `None` when
      converting models to JSON, ensuring compatibility with API responses and
      persistence layers.
    - Acts as the shared parent for specialized DTOs such as:
        * `CreateDto` – defines creation payloads.
        * `UpdateDto` – defines partial updates.
        * `WhereDto` – defines query filters.

    Example
    -------
        from dddk.types.null import Null
        from dddk.types.null_or import NullOr

        class UserDto(BaseDto):
            id: int
            name: NullOr[str] = Null

        user = UserDto(id=1)
        print(user.model_dump_json())  # {"id": 1, "name": null}

    Notes
    -----
    - The `@field_serializer` hook ensures that the internal domain sentinel
      `Null` is transparently converted to `null` (JSON-compatible) during
      serialization.
    - Subclasses should be pure data structures — no business logic should be
      embedded in DTOs.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("*", when_used="json")
    def _serialize_typenull(self, v, _):
        if v == Null:
            return None
        return v

    def get[T](self, attr: str, expected_type: type[T]) -> T:
        if not hasattr(self, attr):
            raise AppError(
                self,
                "KeyError",
                f'Attr "{attr}" Not Exist On {self.__class__.__name__}',
                code=500,
            )

        data = getattr(self, attr)
        if not isinstance(data, expected_type):
            raise AppError(
                self,
                "TypeError",
                f'Attr "{attr}" Not Satisfy Expected Type "{expected_type.__name__}" On {self.__class__.__name__}',
                code=500,
            )

        return data
