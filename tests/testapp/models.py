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

    class Meta:
        app_label = "testapp"

    def as_dto(self) -> GadgetDto:
        return GadgetDto(
            uuid=str(self.uuid),
            name=self.name,
            widget_id=str(self.widget_id),
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
        )
