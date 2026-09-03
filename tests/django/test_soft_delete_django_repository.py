from uuid import (
    uuid4,
)

import pytest

from dddk import (
    AppError,
)
from tests.testapp.dtos import (
    GadgetWhereDto,
    WidgetWhereDto,
    GadgetUpdateDto,
    WidgetCreateDto,
    WidgetUpdateDto,
)
from tests.testapp.models import (
    Gadget,
    Widget,
)
from tests.testapp.repositories import (
    GadgetRepository,
    WidgetRepository,
    GadgetWithSelectRelatedRepository,
)

pytestmark = pytest.mark.django_db


def test_create_persists_and_returns_dto():
    repository = WidgetRepository()

    dto = repository.create(WidgetCreateDto(name="widget-1"))

    assert dto.name == "widget-1"
    assert Widget.objects.filter(pk=dto.uuid).exists()


def test_create_many_persists_all_and_returns_query_response():
    repository = WidgetRepository()

    result = repository.create_many(
        [WidgetCreateDto(name="a"), WidgetCreateDto(name="b")]
    )

    assert {dto.name for dto in result.all} == {"a", "b"}
    assert Widget.objects.count() == 2


def test_create_many_with_empty_list_returns_empty_query_response():
    repository = WidgetRepository()
    result = repository.create_many([])
    assert result.all == []
    assert Widget.objects.count() == 0


def test_find_without_filters_returns_only_active_records():
    active = Widget.objects.create(name="active")
    deleted = Widget.objects.create(name="deleted")
    deleted.soft_delete()

    result = WidgetRepository().find(WidgetWhereDto())

    assert {dto.uuid for dto in result.all} == {str(active.uuid)}


def test_find_by_uuid_field():
    widget = Widget.objects.create(name="widget")
    Widget.objects.create(name="other")

    result = WidgetRepository().find(WidgetWhereDto(uuid=str(widget.uuid)))

    assert [dto.uuid for dto in result.all] == [str(widget.uuid)]


def test_find_by_uuids_list():
    w1 = Widget.objects.create(name="w1")
    w2 = Widget.objects.create(name="w2")
    Widget.objects.create(name="w3")

    result = WidgetRepository().find(
        WidgetWhereDto(uuids=[str(w1.uuid), str(w2.uuid)])
    )

    assert {dto.uuid for dto in result.all} == {str(w1.uuid), str(w2.uuid)}


def test_find_with_empty_uuids_list_returns_empty_without_querying_all():
    Widget.objects.create(name="w1")

    result = WidgetRepository().find(WidgetWhereDto(uuids=[]))

    assert result.all == []


def test_find_by_custom_field():
    Widget.objects.create(name="alice")
    Widget.objects.create(name="bob")

    result = WidgetRepository().find(WidgetWhereDto(name="alice"))

    assert [dto.name for dto in result.all] == ["alice"]


def test_find_by_fk_id_suffix_field():
    widget = Widget.objects.create(name="widget")
    other_widget = Widget.objects.create(name="other")
    gadget = Gadget.objects.create(name="gadget-1", widget=widget)
    Gadget.objects.create(name="gadget-2", widget=other_widget)

    result = GadgetRepository().find(
        GadgetWhereDto(widget_id=str(widget.uuid))
    )

    assert [dto.uuid for dto in result.all] == [str(gadget.uuid)]


def test_find_uses_where_field_to_filter_mapping():
    widget = Widget.objects.create(name="north-widget")
    gadget = Gadget.objects.create(name="gadget-1", widget=widget)
    other_widget = Widget.objects.create(name="south-widget")
    Gadget.objects.create(name="gadget-2", widget=other_widget)

    result = GadgetRepository().find(
        GadgetWhereDto(widget_name="north-widget")
    )

    assert [dto.uuid for dto in result.all] == [str(gadget.uuid)]


def test_update_changes_only_provided_fields():
    widget = Widget.objects.create(name="old-name")

    updated = WidgetRepository().update(
        str(widget.uuid), WidgetUpdateDto(name="new-name")
    )

    assert updated.name == "new-name"
    widget.refresh_from_db()
    assert widget.name == "new-name"


def test_update_ignores_null_fields():
    widget = Widget.objects.create(name="unchanged")

    updated = WidgetRepository().update(str(widget.uuid), WidgetUpdateDto())

    assert updated.name == "unchanged"


def test_update_supports_fk_id_suffix_field():
    widget_a = Widget.objects.create(name="a")
    widget_b = Widget.objects.create(name="b")
    gadget = Gadget.objects.create(name="gadget", widget=widget_a)

    updated = GadgetRepository().update(
        str(gadget.uuid), GadgetUpdateDto(widget_id=str(widget_b.uuid))
    )

    assert updated.widget_id == str(widget_b.uuid)


def test_update_raises_app_error_when_not_found():
    with pytest.raises(AppError) as exc_info:
        WidgetRepository().update(str(uuid4()), WidgetUpdateDto(name="x"))
    assert exc_info.value.code == 404


def test_delete_soft_deletes_and_returns_id():
    widget = Widget.objects.create(name="widget")

    deleted_id = WidgetRepository().delete(str(widget.uuid))

    assert deleted_id == str(widget.uuid)
    widget.refresh_from_db()
    assert widget.deleted_at is not None
    assert Widget.objects.filter(pk=widget.pk).exists() is False


def test_delete_raises_app_error_when_not_found():
    with pytest.raises(AppError) as exc_info:
        WidgetRepository().delete(str(uuid4()))
    assert exc_info.value.code == 404


def test_find_without_select_related_fields_queries_related_row_per_result(
    django_assert_num_queries,
):
    owner = Widget.objects.create(name="owner")
    widget = Widget.objects.create(name="widget")
    for i in range(3):
        Gadget.objects.create(name=f"gadget-{i}", widget=widget, owner=owner)

    with django_assert_num_queries(4):
        result = GadgetRepository().find(GadgetWhereDto())

    assert {dto.owner_id for dto in result.all} == {str(owner.uuid)}


def test_find_with_select_related_fields_avoids_query_per_result(
    django_assert_num_queries,
):
    owner = Widget.objects.create(name="owner")
    widget = Widget.objects.create(name="widget")
    for i in range(3):
        Gadget.objects.create(name=f"gadget-{i}", widget=widget, owner=owner)

    with django_assert_num_queries(1):
        result = GadgetWithSelectRelatedRepository().find(GadgetWhereDto())

    assert {dto.owner_id for dto in result.all} == {str(owner.uuid)}


def test_find_with_select_related_fields_returns_none_for_soft_deleted_owner():
    owner = Widget.objects.create(name="owner")
    widget = Widget.objects.create(name="widget")
    Gadget.objects.create(name="gadget", widget=widget, owner=owner)
    owner.soft_delete()

    result = GadgetWithSelectRelatedRepository().find(GadgetWhereDto())

    assert [dto.owner_id for dto in result.all] == [None]


def test_find_with_select_related_fields_returns_none_for_null_owner():
    widget = Widget.objects.create(name="widget")
    Gadget.objects.create(name="gadget", widget=widget)

    result = GadgetWithSelectRelatedRepository().find(GadgetWhereDto())

    assert [dto.owner_id for dto in result.all] == [None]
