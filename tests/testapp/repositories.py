from tests.testapp.dtos import (
    GadgetDto,
    WidgetDto,
    GadgetWhereDto,
    WidgetWhereDto,
    GadgetCreateDto,
    GadgetUpdateDto,
    WidgetCreateDto,
    WidgetUpdateDto,
)
from tests.testapp.models import (
    Gadget,
    Widget,
)
from dddk.crud.django.soft_delete_django_repository import (
    SoftDeleteDjangoRepository,
)


class WidgetRepository(
    SoftDeleteDjangoRepository[
        Widget,
        WidgetDto,
        WidgetWhereDto,
        WidgetCreateDto,
        WidgetUpdateDto,
        WidgetDto,
    ]
):
    response = WidgetDto
    model = Widget
    dto = WidgetDto


class GadgetRepository(
    SoftDeleteDjangoRepository[
        Gadget,
        GadgetDto,
        GadgetWhereDto,
        GadgetCreateDto,
        GadgetUpdateDto,
        GadgetDto,
    ]
):
    response = GadgetDto
    model = Gadget
    dto = GadgetDto
    where_field_to_filter = {
        "widget_name": "widget__name",
    }
