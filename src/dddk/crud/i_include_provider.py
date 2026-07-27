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
from dddk.crud.tools.query_response import (
    QueryResponse,
)

RESPONSE = TypeVar("RESPONSE", bound=BaseDto)
WHERE = TypeVar("WHERE", bound=WhereDto)


class IIncludeProvider(ABC, Generic[WHERE, RESPONSE]):
    @abstractmethod
    def include(
        self, dtos: QueryResponse[RESPONSE, WHERE]
    ) -> QueryResponse[RESPONSE, WHERE]:
        """
        Populate relational fields (includes) in flat DTOs returned by a repository.

        This provider receives a query result composed of flat DTOs (i.e., without
        relational data populated) and enriches them by resolving related entities
        using bulk database queries. Repositories and model `as_dto()` methods must
        always return flat DTOs; all include logic is centralized in this layer.

        Implementations must resolve relations in batches using identifiers already
        present in the DTOs (e.g., foreign keys or entity ids) and inject the related
        data into the corresponding DTO fields in memory. Per-item database queries
        are strictly forbidden.

        This provider must not:
        - Perform filtering, pagination, or ordering.
        - Modify ORM model instances.
        - Issue database queries inside loops.
        - Change the structure or metadata of the original query response.

        The returned `QueryResponse` must preserve the original query context
        (table name, WHERE criteria, pagination metadata, etc.), differing only
        by having the requested relational fields populated.

        Args:
            dtos (QueryResponse[RESPONSE, WHERE]):
                Repository query result containing flat DTOs and query metadata.

        Returns:
            QueryResponse[RESPONSE, WHERE]:
                Query result with the same metadata and DTOs enriched with
                resolved relational data.
        """
        ...
