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

PIVOT_DTO = TypeVar("PIVOT_DTO", bound=BaseDto)
PIVOT_WHERE = TypeVar("PIVOT_WHERE", bound=WhereDto)
PIVOT_CREATE = TypeVar("PIVOT_CREATE", bound=CreateDto)
PIVOT_UPDATE = TypeVar("PIVOT_UPDATE", bound=UpdateDto)
PIVOT_RESPONSE = TypeVar("PIVOT_RESPONSE", bound=BaseDto)

REL_DTO = TypeVar("REL_DTO", bound=BaseDto)
REL_WHERE = TypeVar("REL_WHERE", bound=WhereDto)
REL_CREATE = TypeVar("REL_CREATE", bound=CreateDto)
REL_UPDATE = TypeVar("REL_UPDATE", bound=UpdateDto)
REL_RESPONSE = TypeVar("REL_RESPONSE", bound=BaseDto)


@dataclass(frozen=True)
class M2MWithPivotRelationConfig(
    Generic[
        PIVOT_DTO,
        PIVOT_WHERE,
        PIVOT_CREATE,
        PIVOT_UPDATE,
        PIVOT_RESPONSE,
        REL_DTO,
        REL_WHERE,
        REL_CREATE,
        REL_UPDATE,
        REL_RESPONSE,
    ]
):
    """
    Configuration for a M2M relation where the pivot/join record is the
    target, enriched with the related entity set onto it.

    Unlike ``M2MRelationConfig`` (which discards the join record and returns
    only the related entities), this config keeps the pivot record and
    populates ``pivot_target_field`` with the resolved related entity —
    useful when the join table carries extra attributes (e.g. ``value``,
    ``order``, ``role``) that the consumer needs alongside the relation.

    Attributes:
        include_field: Name of the boolean flag on the ``include`` DTO that
            enables this relation (e.g. ``"respondent_tags"``).  The loader
            skips this config when the flag is falsy.
        parent_id_field: Field on the parent DTO that holds its own identity
            (e.g. ``"uuid"``).  Used to collect the batch of parent IDs
            passed to the pivot-table query.
        target_field: Field on the parent DTO where the enriched pivot list
            will be assigned (e.g. ``"respondent_tags"``).
        pivot_repository: Repository for the pivot/join table.  Its ``find``
            must return a ``QueryResponse``.
        pivot_where_dto: ``WhereDto`` class used to build the batch filter
            for the pivot-table query.
        pivot_where_parent_ids_field: Field on ``pivot_where_dto`` that
            accepts a list of parent IDs for the batch lookup (e.g.
            ``"respondent_ids"`` mapped to ``respondent_id__in`` via
            ``where_field_to_filter``).
        pivot_parent_id_field: Field on each pivot DTO that references the
            parent (e.g. ``"respondent"``).  Must resolve to a plain ``str``
            UUID so pivot records can be grouped by parent.
        pivot_related_id_field: Field on each pivot DTO that references the
            related entity (e.g. ``"respondent_tag"``).  Must resolve to a
            plain ``str`` UUID used to fetch the related objects.
        pivot_target_field: Field on each pivot DTO where the resolved
            related entity will be assigned (e.g. ``"respondent_tag"``).
            Set via ``setattr`` at runtime.
        relation_repository: Repository for the related entity.  Its ``find``
            must return a ``QueryResponse``.
        relation_where_dto: ``WhereDto`` class used to build the batch filter
            for the related-entity query.
        relation_where_ids_field: Field on ``relation_where_dto`` that accepts
            a list of related IDs for the batch lookup.  Defaults to ``"ids"``
            which ``SoftDeleteDjangoRepository`` maps to ``id__in``.
        relation_id_field: Field on each related-entity DTO used as the lookup
            key when building ``related_by_id``.  Defaults to ``"id"``; use
            ``"uuid"`` for models whose primary key is exposed as ``uuid``.
    """

    include_field: str
    parent_id_field: str
    target_field: str

    # Pivot / join table
    pivot_repository: IRepository[
        PIVOT_DTO, PIVOT_WHERE, PIVOT_CREATE, PIVOT_UPDATE, PIVOT_RESPONSE
    ]
    pivot_where_dto: type[PIVOT_WHERE]
    pivot_where_parent_ids_field: str
    pivot_parent_id_field: str
    pivot_related_id_field: str
    pivot_target_field: str

    # Related entity
    relation_repository: IRepository[
        REL_DTO, REL_WHERE, REL_CREATE, REL_UPDATE, REL_RESPONSE
    ]
    relation_where_dto: type[REL_WHERE]
    relation_where_ids_field: str = "ids"
    relation_id_field: str = "id"
