from typing import (
    TypeVar,
)

from dddk.types.base_dto import (
    BaseDto,
)
from dddk.crud.django.soft_delete_model import (
    SoftDeleteModel,
)

DTO = TypeVar("DTO", bound=BaseDto)


def get_if_active(model: SoftDeleteModel) -> str | None:
    if model.deleted_at is not None:
        return None
    return str(model.uuid)
