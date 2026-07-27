from typing import (
    TypeVar,
)
from collections import (
    defaultdict,
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

DTO = TypeVar("DTO", bound=BaseDto)


def populate_m2m_relations(
    dtos: list[DTO],
    dto_relation_field: str,
    m2m_repository: IRepository,
    m2m_where: type[WhereDto],
    m2m_where_parent_ids_field: str,
    m2m_parent_id_field: str,
    m2m_related_id_field: str,
    relation_repository: IRepository,
    relation_where: type[WhereDto],
    relation_where_ids_field: str = "ids",
) -> list[DTO]:
    """
    Populate a many-to-many relation field in a list of DTOs using repository queries.

    This utility performs a generic population of many-to-many relations by executing
    two repository queries:

    1. Query the many-to-many relation repository to obtain pairs of
       (parent_id, related_id).
    2. Query the related entity repository to retrieve the DTOs corresponding
       to the collected related_ids.

    The function then groups related entities by their parent id and assigns or
    extends the relation field in each DTO.

    This approach avoids N+1 queries by performing batched lookups and can be
    reused for any many-to-many relation as long as the repositories follow the
    project's DTO and `WhereDto` conventions.

    Args:
        dtos (List[DTO]):
            List of DTOs whose relations should be populated. Each DTO must
            contain an `id` attribute.

        dto_relation_field (str):
            Name of the field in the DTO where the related entities will be
            assigned or extended.

        m2m_repository (IRepository):
            Repository responsible for querying the many-to-many relation table.

        m2m_where (Type[WhereDto]):
            WhereDto class used to filter the many-to-many relation query.

        m2m_where_parent_ids_field (str):
            Field name in the `m2m_where` DTO used to filter by parent ids
            (typically something like `"label_ids"` or `"user_ids"`).

        m2m_parent_id_field (str):
            Attribute name in the returned relation DTO that contains the
            parent id.

        m2m_related_id_field (str):
            Attribute name in the returned relation DTO that contains the
            related entity id.

        relation_repository (IRepository):
            Repository used to retrieve the related entities.

        relation_where (Type[WhereDto]):
            WhereDto class used to filter the related entities query.

        relation_where_ids_field (str, optional):
            Field name in the `relation_where` DTO used to filter by ids.
            Defaults to `"ids"`.

    Returns:
        List[DTO]:
            The same list of DTOs with their relation field populated
            (or extended if already initialized).

    Notes:
        - DTOs must expose an `id` attribute.
        - The relation field in the DTO must either be `None` or a list.
        - The function performs batched queries to minimize database calls.
        - Existing relations in the DTO field are preserved and extended.
    """

    if not dtos:
        return dtos

    parent_ids = [getattr(dto, "id") for dto in dtos]

    related_ids_by_parent_id: dict[str, list[str]] = defaultdict(list)
    related_ids: set[str] = set()

    m2m_filter = m2m_where()
    setattr(m2m_filter, m2m_where_parent_ids_field, parent_ids)

    found_m2m_relations = m2m_repository.find(m2m_filter)

    for relation in found_m2m_relations:
        parent_id = getattr(relation, m2m_parent_id_field, None)
        related_id = getattr(relation, m2m_related_id_field, None)

        if isinstance(parent_id, str) and isinstance(related_id, str):
            related_ids_by_parent_id[parent_id].append(related_id)
            related_ids.add(related_id)

    if not related_ids:
        return dtos

    relation_filter = relation_where()
    setattr(relation_filter, relation_where_ids_field, list(related_ids))

    related_by_id = {
        related.id: related
        for related in relation_repository.find(relation_filter)
    }

    for dto in dtos:
        dto_related_ids = related_ids_by_parent_id.get(getattr(dto, "id"), [])
        if not dto_related_ids:
            continue

        relateds = [
            related_by_id[related_id]
            for related_id in dto_related_ids
            if related_id in related_by_id
        ]

        if not relateds:
            continue

        current_relations = getattr(dto, dto_relation_field, None)

        if current_relations is None:
            setattr(dto, dto_relation_field, relateds)
        else:
            current_relations.extend(relateds)

    return dtos
