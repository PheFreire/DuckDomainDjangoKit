from typing import (
    TYPE_CHECKING,
)

from dddk.crud.dtos import (
    WhereDto,
    CreateDto,
    UpdateDto,
)
from dddk.types.null import (
    Null,
)
from dddk.types.null_or import (
    NullOr,
)
from dddk.types.base_dto import (
    BaseDto,
)
from dddk.error.app_error import (
    AppError,
)
from dddk.relations_loader import (
    RelationLoader,
    FkRelationConfig,
    M2MRelationConfig,
    RelationLoaderConfig,
    RelationLoaderResult,
    HasManyRelationConfig,
    M2MWithPivotRelationConfig,
)
from dddk.crud.i_repository import (
    IRepository,
)
from dddk.types.request_dto import (
    RequestDto,
)
from dddk.envs.interfaces.i_envs import (
    IEnvs,
)
from dddk.crud.tools.query_response import (
    QueryResponse,
)
from dddk.crud.tools.populate_fk_relations import (
    populate_fk_relations,
)

if TYPE_CHECKING:
    from dddk.crud.django import (
        SoftDeleteAdmin,
        SoftDeleteModel,
        SoftDeleteDjangoRepository,
    )
    from dddk.crud.django.utils import (
        get_if_active,
    )

__all__ = [
    "AppError",
    "BaseDto",
    "Null",
    "NullOr",
    "RequestDto",
    "CreateDto",
    "UpdateDto",
    "WhereDto",
    "SoftDeleteModel",
    "SoftDeleteDjangoRepository",
    "SoftDeleteAdmin",
    "get_if_active",
    "IEnvs",
    "IRepository",
    "QueryResponse",
    "populate_fk_relations",
    "RelationLoader",
    "FkRelationConfig",
    "HasManyRelationConfig",
    "M2MRelationConfig",
    "M2MWithPivotRelationConfig",
    "RelationLoaderConfig",
    "RelationLoaderResult",
]


def __getattr__(name: str):
    if name in (
        "SoftDeleteDjangoRepository",
        "SoftDeleteModel",
        "SoftDeleteAdmin",
        "get_if_active",
    ):
        from dddk.crud.django import (  # noqa: F401
            SoftDeleteAdmin,
            SoftDeleteModel,
            SoftDeleteDjangoRepository,
        )
        from dddk.crud.django.utils import (  # noqa: F401
            get_if_active,
        )

        globals()[name] = locals()[name]
        return locals()[name]
    raise AttributeError(f"module 'dddk' has no attribute '{name}'")
