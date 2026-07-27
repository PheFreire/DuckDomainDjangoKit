import re

from pydantic import (
    Field,
    BaseModel,
    field_validator,
)

from dddk.error.app_error import (
    AppError,
)


class DatabaseSettingsDto(BaseModel):
    """
    DTO that represents the database access URL configuration.

    Attributes:
        url (str): Full URL in the expected database connection format.
    """

    url: str = Field(
        ...,
        description="Full database connection URL (e.g., postgres://user:pass@host:5432/dbname)",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        pattern = re.compile(
            r"^(?:postgres(?:ql)?|mysql|sqlite|oracle|mssql|postgresql\+psycopg)://"
            r"(?:[^:@]+(?::[^@]*)?@)?"
            r"[^:/?#]*"
            r"(?:\:\d+)?"
            r"(?:\/[^?#]*)?"
            r"(?:\?[^#]*)?"
            r"(?:\#.*)?$"
        )

        if not pattern.match(value):
            raise AppError(
                class_pointer=cls,
                title="Invalid DATABASE_URL format error",
                message="The provided database URL does not match the expected format.",
                details={"invalid_value": value},
                code=400,
            )

        return value
