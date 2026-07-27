from abc import (
    abstractmethod,
)
from uuid import (
    uuid4,
)

from django.db import (
    models,
)

from dddk.types.base_dto import (
    BaseDto,
)
from dddk.crud.django.soft_delete_table import (
    SoftDeleteTable,
)


class SoftDeleteModel(SoftDeleteTable):
    """
    Abstract base model that combines Soft Delete behavior with domain-level
    serialization capabilities.

    This class should be inherited by any Django model that belongs to a domain
    layer. It provides:
      - Native Soft Delete support, inherited from `SoftDeleteTable`;
      - A default UUID primary key field (`id`);
      - An abstract method `as_dto()` that enforces conversion of ORM entities
        into domain Data Transfer Objects (DTOs).

    Attributes
    ----------
    id : UUIDField
        Unique identifier for the record. Automatically generated using `uuid4`
        and set as the primary key.

    Methods
    -------
    as_dto(include_fks: bool = False, show_deleted: bool = False) -> BaseDto
        Abstract method that must be implemented by subclasses to serialize
        the Django model instance into a domain DTO (derived from `BaseDto`).
        The `include_fks` flag determines whether foreign-key relationships
        should be included in the serialization.
        The `show_deleted` flag indicates whether logically deleted records
        should be included in the DTO representation.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True
        app_label = "duck_domain"

    @abstractmethod
    def as_dto(self) -> BaseDto:
        """
        Serialize the current Django model instance into a domain DTO (BaseDto).

        Returns
        -------
        BaseDto
            A Pydantic model representing the corresponding domain entity.

        Raises
        ------
        NotImplementedError
            If the subclass does not override this method.
        """
        raise NotImplementedError(
            "Subclasses must implement `as_dto`, returning a BaseDto instance."
        )
