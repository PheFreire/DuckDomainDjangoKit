from typing import (
    Generic,
    TypeVar,
)
from dataclasses import (
    dataclass,
)

from dddk.types.base_dto import (
    BaseDto,
)
from dddk.crud.i_repository import (
    IRepository,
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

HM_DTO = TypeVar("HM_DTO", bound=BaseDto)
HM_WHERE = TypeVar("HM_WHERE", bound=WhereDto)
HM_CREATE = TypeVar("HM_CREATE", bound=CreateDto)
HM_UPDATE = TypeVar("HM_UPDATE", bound=UpdateDto)
HM_RESPONSE = TypeVar("HM_RESPONSE", bound=BaseDto)


@dataclass(frozen=True)
class HasManyRelationConfig(
    Generic[HM_DTO, HM_WHERE, HM_CREATE, HM_UPDATE, HM_RESPONSE]
):
    """
    Configuration for a one-to-many (has-many) relation.

    Unlike ``M2MRelationConfig``, here the child records are the final target —
    there is no separate related entity to fetch through a join table.
    A single batch query retrieves all children filtered by parent IDs, then
    groups them by ``child_parent_id_field`` and assigns the list to each parent.

    Example: ``Respondent → [Answer]`` — one query fetches all answers whose
    ``respondent_id`` is in the set of parent respondent UUIDs, then each
    respondent gets its own slice of that result.

    Attributes:
    -----------
    include_field: Name of the boolean flag on the `include` DTO that enables this relation. The loader skips this config when the flag is falsy.
    parent_id_field: Field on the parent DTO that holds its own identity. Used to collect the batch of parent IDs passed to the child repository.
    target_field: Field on the parent DTO where the matched child list will be assigned.
    child_parent_id_field: Field on each child DTO that references the parent ID.  Must resolve to a plain `str` UUID at runtime so children can be grouped by parent.
    repository: Repository for the child entity.
    where_dto: `WhereDto` class used to build the batch filter for the child query.
    where_parent_ids_field: Field on `where_dto` that accepts a list of parent IDs for the batch lookup.
    """

    include_field: str
    parent_id_field: str
    target_field: str
    child_parent_id_field: str

    repository: IRepository[
        HM_DTO, HM_WHERE, HM_CREATE, HM_UPDATE, HM_RESPONSE
    ]
    where_dto: type[HM_WHERE]
    where_parent_ids_field: str
