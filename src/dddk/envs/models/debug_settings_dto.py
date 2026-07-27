from pydantic import (
    Field,
    BaseModel,
)


class DebugSettingsDto(BaseModel):
    """
    DTO representing the system's debug configuration.

    Attributes:
        is_active (bool): Indicates whether debug mode is enabled.
        labels (List[str]): A list of enabled debug labels used to control conditional breakpoints.
        levels (List[str]): A list of debug levels to filter logs or trigger conditional behaviors
                            based on severity or category.
    """

    is_active: bool = Field(
        default=False, description="Indicates whether debug mode is enabled."
    )
    labels: list[str] = Field(
        default_factory=list,
        description="A list of enabled debug labels used to control conditional breakpoints.",
    )
    levels: list[str] = Field(
        default_factory=list,
        description="A list of debug levels to filter logs or trigger conditional behaviors based on severity or category.",
    )
