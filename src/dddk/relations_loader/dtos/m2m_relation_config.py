from __future__ import (
    annotations,
)

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

M2M_DTO = TypeVar("M2M_DTO", bound=BaseDto)
M2M_WHERE = TypeVar("M2M_WHERE", bound=WhereDto)
M2M_CREATE = TypeVar("M2M_CREATE", bound=CreateDto)
M2M_UPDATE = TypeVar("M2M_UPDATE", bound=UpdateDto)
M2M_RESPONSE = TypeVar("M2M_RESPONSE", bound=BaseDto)

REL_DTO = TypeVar("REL_DTO", bound=BaseDto)
REL_WHERE = TypeVar("REL_WHERE", bound=WhereDto)
REL_CREATE = TypeVar("REL_CREATE", bound=CreateDto)
REL_UPDATE = TypeVar("REL_UPDATE", bound=UpdateDto)
REL_RESPONSE = TypeVar("REL_RESPONSE", bound=BaseDto)


@dataclass(frozen=True)
class M2MRelationConfig(
    Generic[
        M2M_DTO,
        M2M_WHERE,
        M2M_CREATE,
        M2M_UPDATE,
        M2M_RESPONSE,
        REL_DTO,
        REL_WHERE,
        REL_CREATE,
        REL_UPDATE,
        REL_RESPONSE,
    ]
):
    """
    Configuration for a Many-to-Many relation resolved through a join table.

    Executes two batch queries: one against the join/pivot table to map parent
    IDs to related IDs, and one against the related entity table to fetch the
    actual objects.  The join record itself is discarded — only the related
    entities are assigned to `target_field` on each parent DTO.

    Use `M2MWithPivotRelationConfig` instead when the join record carries
    extra attributes (e.g. `value`, `order`) that the consumer needs.

    Example: `Respondent → [Application]` via `RespondentApplication` —
    the join table maps respondent IDs to application IDs; a second query
    fetches the `ApplicationDto` objects, which are then set on each
    respondent's `applications` field.

    Attributes:
    -----------
    `include_field`:
        Name of the boolean flag on the `include` DTO that enables this relation.
        The loader skips this config when the flag is falsy.

    `parent_id_field`:
        Field on the parent DTO that holds its own identity.
        Used to collect the batch of parent IDs passed to the join-table query.

    `target_field`:
        Field on the parent DTO where the list of resolved related objects will be assigned.

    `m2m_repository`:
        Repository for the join/pivot table.
        Its `find` must return a `QueryResponse`.

    `m2m_where_dto`:
        `WhereDto` class used to build the batch filter for the join-table query.

    `m2m_where_parent_ids_field`:
        Field on `m2m_where_dto` that accepts a list of parent IDs for the batch lookup.

    `m2m_parent_id_field`:
        Field on each join-table DTO that references the parent.
        Must resolve to a plain `str` UUID so records can be grouped by parent.

    `m2m_related_id_field`:
        Field on each join-table DTO that references the related entity.
        Must resolve to a plain `str` UUID used to fetch the related objects.

    `relation_id_field`:
        Field on the relation DTO that holds its own identity.

    `relation_repository`:
        Repository for the related entity.
        Its `find` must return a `QueryResponse`.

    `relation_where_dto`:
        `WhereDto` class used to build the batch filter for the related-entity query.

    `relation_where_ids_field`:
        Field on `relation_where_dto` that accepts a list of related IDs for the batch lookup.
        Defaults to `"ids"` which `SoftDeleteDjangoRepository` maps to `id__in`.
    """

    include_field: str
    parent_id_field: str
    target_field: str

    m2m_repository: IRepository[
        M2M_DTO, M2M_WHERE, M2M_CREATE, M2M_UPDATE, M2M_RESPONSE
    ]
    m2m_where_dto: type[M2M_WHERE]
    m2m_where_parent_ids_field: str
    m2m_parent_id_field: str
    m2m_related_id_field: str

    relation_id_field: str
    relation_repository: IRepository[
        REL_DTO, REL_WHERE, REL_CREATE, REL_UPDATE, REL_RESPONSE
    ]
    relation_where_dto: type[REL_WHERE]
    relation_where_ids_field: str = "ids"
