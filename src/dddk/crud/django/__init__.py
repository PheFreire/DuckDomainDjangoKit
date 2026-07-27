from dddk.crud.django.soft_delete_admin import (
    SoftDeleteAdmin,
)
from dddk.crud.django.soft_delete_model import (
    SoftDeleteModel,
)
from dddk.crud.django.soft_delete_django_repository import (
    SoftDeleteDjangoRepository,
)

__all__ = [
    "SoftDeleteDjangoRepository",
    "SoftDeleteModel",
    "SoftDeleteAdmin",
]
