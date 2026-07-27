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

FK_DTO = TypeVar("FK_DTO", bound=BaseDto)
FK_WHERE = TypeVar("FK_WHERE", bound=WhereDto)
FK_CREATE = TypeVar("FK_CREATE", bound=CreateDto)
FK_UPDATE = TypeVar("FK_UPDATE", bound=UpdateDto)
FK_RESPONSE = TypeVar("FK_RESPONSE", bound=BaseDto)


@dataclass(frozen=True)
class FkRelationConfig(
    Generic[FK_DTO, FK_WHERE, FK_CREATE, FK_UPDATE, FK_RESPONSE]
):
    """
    Configuration for a Foreign Key (many-to-one) relation.

    Used when the parent DTO holds a scalar ID pointing to a single related
    entity.  The loader collects all source IDs in one pass, fetches the
    related entities in a single batch query, then sets ``target_field`` on
    each parent DTO with the resolved object.

    Example: ``Answer.respondent_id → RespondentDto`` — every answer carries
    a ``respondent_id``; a single query retrieves all referenced respondents
    and populates ``answer.respondent`` for each record.

    Attributes:
        include_field: Name of the boolean flag on the ``include`` DTO that
            enables this relation (e.g. ``"respondent"``).  The loader skips
            this config when the flag is falsy.
        source_id_field: Field on the parent DTO that holds the FK value —
            the ID of the related entity (e.g. ``"respondent_id"``).  Must
            resolve to a plain ``str`` UUID; non-string values are skipped.
        target_field: Field on the parent DTO where the resolved related
            object will be assigned (e.g. ``"respondent"``).
        repository: Repository for the related entity.  Its ``find`` must
            return a ``QueryResponse``.
        where_dto: ``WhereDto`` class used to build the batch filter for the
            related entity.
        where_ids_field: Field on ``where_dto`` that accepts a list of IDs
            for the batch lookup.  Defaults to ``"ids"`` which
            ``SoftDeleteDjangoRepository`` maps to ``id__in``.
        relation_id_field: Field on the related entity DTO used to build the
            lookup index.  Defaults to ``"uuid"`` which is the standard
            identifier field across project DTOs.
    """

    include_field: str
    source_id_field: str
    target_field: str
    repository: IRepository[
        FK_DTO, FK_WHERE, FK_CREATE, FK_UPDATE, FK_RESPONSE
    ]
    where_dto: type[FK_WHERE]
    where_ids_field: str = "ids"
    relation_id_field: str = "uuid"
