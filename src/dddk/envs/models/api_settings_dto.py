from pydantic import (
    Field,
    BaseModel,
)


class ApiSettingsDto(BaseModel):
    """
    DTO representing the system's API configuration.

    Attributes:
        allowed_hosts (List[str]): A list of allowed hostnames or IPs that are permitted
        to make requests to the API. Used to restrict cross-origin and direct access.
    """

    allowed_hosts: list[str] = Field(
        default=[],
        description="List of hostnames or IPs allowed to access the API.",
    )
    cors_allowed_hosts: list[str] = Field(
        default=[],
        description="List of hostnames or IPs allowed to access the API.",
    )
