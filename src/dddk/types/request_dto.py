from typing import (
    Any,
    Self,
)

from pydantic import (
    ConfigDict,
    ValidationError,
)

from dddk.types.base_dto import (
    BaseDto,
)
from dddk.error.app_error import (
    AppError,
)


class RequestDto(BaseDto):
    """
    Base Data Transfer Object (DTO) for handling external input data, typically
    from HTTP requests or API payloads.

    This class extends `BaseDto` with stricter validation rules suitable for
    request-level DTOs. It forbids any extra fields that are not explicitly
    defined in the model and provides a helper method to validate input data
    and raise domain-friendly errors when validation fails.

    Features
    --------
    - Uses Pydantic's configuration `extra="forbid"` to reject unexpected fields.
    - Converts Pydantic `ValidationError` exceptions into domain-specific
      `AppError` exceptions for consistent error handling across layers.
    - Prints structured validation details (useful for debugging or logging).

    Example
    -------
        from dddk.error.app_error import AppError

        class CreateUserRequest(RequestDto):
            name: str
            email: str

        try:
            user = CreateUserRequest.validate_or_error({
                "name": "Alice",
                "email": 123   # invalid type
            })
        except AppError as e:
            print(e.details)
            # {
            #   "provided": {"name": "Alice", "email": 123},
            #   "error": [{"type": "string_type", "loc": ["email"], ...}]
            # }

    Notes
    -----
    - The `validate_or_error()` method is a convenience wrapper around
      Pydantic's validation, automatically converting errors into
      `AppError` objects with HTTP-friendly metadata (`code=422`).
    - This class is typically used at the application or API boundary to
      ensure that only validated, domain-compatible data enters the system.
    """

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def validate_or_error(cls, data: dict[str, Any]) -> Self:
        """
        Validate incoming data and raise a domain-level `AppError` if invalid.

        Parameters
        ----------
        data : Dict[str, Any]
            The raw input data (typically parsed from an HTTP request body).

        Returns
        -------
        Self
            A validated DTO instance of the calling subclass.

        Raises
        ------
        AppError
            If Pydantic validation fails. The error includes:
              - `provided`: The original input data.
              - `error`: A structured list of validation issues.
              - `code`: 422 (Unprocessable Entity).
        """
        try:
            return cls(**data)
        except ValidationError as e:
            details = {
                "provided": data,
                "error": e.errors(),
            }
            raise AppError(
                cls.__name__,
                "Error: Could Not Instance Request",
                "Invalid input data",
                details,
                code=422,
            )
