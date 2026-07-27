from typing import (
    TypeVar,
)

from dddk.types.base_dto import (
    BaseDto,
)
from dddk.error.app_error import (
    AppError,
)
from dddk.crud.i_repository import (
    IRepository,
)
from dddk.crud.dtos.where_dto import (
    WhereDto,
)

DTO = TypeVar("DTO", bound=BaseDto)


def populate_fk_relations(
    dtos: list[DTO],
    attr: str,
    repository: IRepository,
    relation_where: type[WhereDto],
) -> list[DTO]:
    relation_ids: set[str] = set()

    for dto in dtos:
        value = getattr(dto, attr)
        if value is not None and isinstance(value, str):
            relation_ids.add(value)

    if not relation_ids:
        return dtos

    where_filter = relation_where()
    if not hasattr(where_filter, "ids"):
        dto_name = dtos[0].__class__.__name__
        raise AppError(
            "populate_relations",
            f"Populate {dto_name} Relation Error",
            f'Cannot populate {dto_name} relations because {relation_where.__name__} missing "ids" field',
            {"dto_name": dto_name, "attr": attr, "where": where_filter},
            code=500,
        )

    setattr(where_filter, "ids", list(relation_ids))
    relations = repository.find(where_filter).all

    relation_by_id = {relation.id: relation for relation in relations}

    for dto in dtos:
        value = getattr(dto, attr)
        if value is not None and isinstance(value, str):
            setattr(dto, attr, relation_by_id.get(value))

    return dtos
