import pytest
from django.test import (
    RequestFactory,
)
from django.contrib import (
    admin,
)
from django.contrib.messages.middleware import (
    MessageMiddleware,
)
from django.contrib.sessions.middleware import (
    SessionMiddleware,
)

from tests.testapp.models import (
    Widget,
)
from dddk.crud.django.soft_delete_admin import (
    DeletedAtFilter,
    SoftDeleteAdmin,
)

pytestmark = pytest.mark.django_db


class WidgetAdmin(SoftDeleteAdmin):
    pass


@pytest.fixture()
def widget_admin():
    return WidgetAdmin(Widget, admin.site)


def _build_request():
    request = RequestFactory().post("/admin/testapp/widget/")
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    MessageMiddleware(lambda r: None).process_request(request)
    return request


def test_get_queryset_returns_everything_including_soft_deleted(widget_admin):
    active = Widget.objects.create(name="active")
    deleted = Widget.objects.create(name="deleted")
    deleted.soft_delete()

    assert set(widget_admin.get_queryset(None)) == {active, deleted}


def test_soft_delete_selected_soft_deletes_records(widget_admin):
    widget = Widget.objects.create(name="widget")

    widget_admin.soft_delete_selected(
        _build_request(), Widget.objects.filter(pk=widget.pk)
    )

    widget.refresh_from_db()
    assert widget.deleted_at is not None


def test_soft_delete_selected_skips_already_deleted_records(widget_admin):
    widget = Widget.objects.create(name="widget")
    widget.soft_delete()
    first_deleted_at = widget.deleted_at

    widget_admin.soft_delete_selected(
        _build_request(), Widget.everything.filter(pk=widget.pk)
    )

    widget.refresh_from_db()
    assert widget.deleted_at == first_deleted_at


def test_restore_selected_clears_deleted_at(widget_admin):
    widget = Widget.objects.create(name="widget")
    widget.soft_delete()

    widget_admin.restore_selected(
        _build_request(), Widget.everything.filter(pk=widget.pk)
    )

    widget.refresh_from_db()
    assert widget.deleted_at is None


def test_restore_selected_skips_already_active_records(widget_admin):
    widget = Widget.objects.create(name="widget")

    widget_admin.restore_selected(
        _build_request(), Widget.everything.filter(pk=widget.pk)
    )

    widget.refresh_from_db()
    assert widget.deleted_at is None


def test_duplicate_selected_creates_copy_with_suffix(widget_admin):
    widget = Widget.objects.create(name="widget")

    widget_admin.duplicate_selected(
        _build_request(), Widget.objects.filter(pk=widget.pk)
    )

    assert Widget.objects.filter(name="widget - Copy").exists()
    assert Widget.objects.count() == 2


def test_duplicate_selected_retries_with_incrementing_suffix_on_conflict(
    widget_admin,
):
    widget = Widget.objects.create(name="widget")
    Widget.objects.create(name="widget - Copy")

    widget_admin.duplicate_selected(
        _build_request(), Widget.objects.filter(pk=widget.pk)
    )

    assert Widget.objects.filter(name="widget - Copy 2").exists()


def test_get_unique_char_fields_detects_unique_char_field(widget_admin):
    assert widget_admin._get_unique_char_fields(Widget) == {"name"}


def test_deleted_at_filter_no_returns_only_active_records():
    active = Widget.objects.create(name="active")
    deleted = Widget.objects.create(name="deleted")
    deleted.soft_delete()

    filter_ = DeletedAtFilter(None, {"deleted": ["no"]}, Widget, None)

    assert list(filter_.queryset(None, Widget.everything.all())) == [active]


def test_deleted_at_filter_yes_returns_only_deleted_records():
    Widget.objects.create(name="active")
    deleted = Widget.objects.create(name="deleted")
    deleted.soft_delete()

    filter_ = DeletedAtFilter(None, {"deleted": ["yes"]}, Widget, None)

    assert list(filter_.queryset(None, Widget.everything.all())) == [deleted]


def test_deleted_at_filter_no_value_returns_everything_unfiltered():
    active = Widget.objects.create(name="active")
    deleted = Widget.objects.create(name="deleted")
    deleted.soft_delete()

    filter_ = DeletedAtFilter(None, {}, Widget, None)

    assert set(filter_.queryset(None, Widget.everything.all())) == {
        active,
        deleted,
    }


def test_deleted_at_filter_lookups():
    filter_ = DeletedAtFilter(None, {}, Widget, None)
    assert filter_.lookups(None, None) == [
        ("no", "Not Deleted"),
        ("yes", "Deleted"),
    ]
