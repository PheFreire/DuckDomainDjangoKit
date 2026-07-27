from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypeVar,
)

from dddk.types.base_dto import (
    BaseDto,
)
from dddk.crud.dtos.where_dto import (
    WhereDto,
)
from dddk.crud.dtos.create_dto import (
    CreateDto,
)
from dddk.crud.dtos.update_dto import (
    UpdateDto,
)
from dddk.crud.tools.query_response import (
    QueryResponse,
)

DTO = TypeVar("DTO", bound=BaseDto)
WHERE = TypeVar("WHERE", bound=WhereDto)
CREATE = TypeVar("CREATE", bound=CreateDto)
UPDATE = TypeVar("UPDATE", bound=UpdateDto)
RESPONSE = TypeVar("RESPONSE", bound=BaseDto)


class IRepository(ABC, Generic[DTO, WHERE, CREATE, UPDATE, RESPONSE]):
    """
    Generic repository interface for managing domain entities.

    This interface defines a strongly typed CRUD contract for data persistence,
    enabling consistent data access patterns across different storage
    implementations (e.g., Django ORM, SQLAlchemy, in-memory databases).

    The generic parameters represent the following DTOs:

        - DTO: Base data transfer object representing the entity itself.
        - WHERE: DTO used for filtering and query criteria.
        - CREATE: DTO containing attributes required to create a new entity.
        - UPDATE: DTO defining updatable fields for an existing entity.
        - RESPONSE: DTO returned from query operations, often enriched with
          relational data.

    Implementations should ensure consistent mapping between DTOs and
    persistence-layer models, while preserving data integrity and soft-delete
    semantics where applicable.
    """

    @abstractmethod
    def create(self, create: CREATE) -> DTO:
        """
        Create a new entity record.

        Args:
            create (CREATE): A DTO containing the data required to create
                a new entity.

        Returns:
            DTO: The newly created entity represented as a DTO.
        """
        ...

    @abstractmethod
    def create_many(self, creates: list[CREATE]) -> QueryResponse[DTO, None]:
        """
        Create a new entity record.

        Args:
            create (CREATE): A DTO containing the data required to create
                a new entity.

        Returns:
            DTO: The newly created entity represented as a DTO.
        """
        ...

    @abstractmethod
    def find(self, where: WHERE) -> QueryResponse[RESPONSE, WHERE]:
        """
        Retrieve a collection of entities that match the given query criteria.

        Args:
            where (WHERE): A DTO representing the filter or query parameters.

        Returns:
            QueryResponse[RESPONSE, WHERE]: A structured response containing the
            list of matching entities and metadata about the executed query.
        """
        ...

    @abstractmethod
    def update(self, id: str, update: UPDATE) -> DTO:
        """
        Update an existing entity record identified by its unique identifier.

        Args:
            id (str): The unique identifier of the entity to be updated.
            update (UPDATE): A DTO specifying which fields should be modified.

        Returns:
            DTO: The updated entity represented as a DTO.
        """
        ...

    @abstractmethod
    def delete(self, id: str) -> str:
        """
        Delete (or soft-delete) an entity record by its unique identifier.

        Args:
            id (str): The unique identifier of the entity to delete.

        Returns:
            str: The id of the deleted entity.
        """
        ...
