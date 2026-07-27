from dddk.types.base_dto import (
    BaseDto,
)


class CreateDto(BaseDto):
    """
    Base Data Transfer Object (DTO) for entity creation operations.

    This class serves as the foundation for all DTOs that define the input
    structure required to create new domain entities. It inherits all
    validation and serialization behavior from `BaseDto`.

    Subclasses should declare the fields that represent the data necessary
    to instantiate and persist a new entity. For example:

        class ResearchCreateDto(CreateDto):
            title: str
            description: str
            author_id: UUID

    Notes
    -----
    - `CreateDto` itself does not implement any logic; it exists to provide
      a clear semantic distinction between DTOs used for creation and those
      used for updates, queries, or responses.
    - Using separate DTO types for different operation contexts improves
      clarity and type safety in domain and application layers.
    """
