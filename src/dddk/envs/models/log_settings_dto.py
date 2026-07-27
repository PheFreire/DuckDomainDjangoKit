from pydantic import (
    Field,
    BaseModel,
)


class LogSettingsDto(BaseModel):
    """
    DTO representing the system's logging configuration.

    Attributes:
        is_active (bool): Indicates whether logging is enabled.
        indent (int): Specifies the indentation level for log formatting.
        labels (List[str]): A list of custom log labels used to categorize and filter log messages.
        levels (List[str]): A list of logging levels to control log filtering,
                            such as 'debug', 'info', 'warning', 'error', and 'critical'.
    """

    is_active: bool = Field(
        default=True, description="Indicates whether logging is enabled."
    )
    indent: int = Field(
        default=3,
        description="Specifies the indentation level for log formatting.",
    )
    labels: list[str] = Field(
        default_factory=list,
        description="A list of custom log labels used to categorize and filter log messages.",
    )
    levels: list[str] = Field(
        default_factory=list,
        description="A list of logging levels to control log filtering, such as 'debug', 'info', 'warning', 'error', and 'critical'.",
    )
