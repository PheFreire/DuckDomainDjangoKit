from django.db import (
    models,
)

from tests.testapp.dtos import (
    GadgetDto,
    WidgetDto,
)
from dddk.crud.django.soft_delete_model import (
    SoftDeleteModel,
)
from dddk.crud.django.utils.get_if_active import (
    get_if_active,
)


class Widget(SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = "testapp"

    def as_dto(self) -> WidgetDto:
        return WidgetDto(
            uuid=str(self.uuid),
            name=self.name,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
        )


class Gadget(SoftDeleteModel):
    name = models.CharField(max_length=100)
    widget = models.ForeignKey(
        Widget, on_delete=models.CASCADE, related_name="gadgets"
    )
    owner = models.ForeignKey(
        Widget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_gadgets",
    )

    class Meta:
        app_label = "testapp"

    def as_dto(self) -> GadgetDto:
        return GadgetDto(
            uuid=str(self.uuid),
            name=self.name,
            widget_id=str(self.widget_id),
            owner_id=get_if_active(self.owner) if self.owner else None,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
        )
