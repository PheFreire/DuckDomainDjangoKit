import pytest
from django.db.models.query import (
    Prefetch,
)

from tests.testapp.models import (
    Gadget,
    Widget,
)

pytestmark = pytest.mark.django_db


def test_objects_manager_excludes_soft_deleted_records():
    active = Widget.objects.create(name="active")
    deleted = Widget.objects.create(name="deleted")
    deleted.soft_delete()

    assert list(Widget.objects.all()) == [active]


def test_everything_manager_includes_soft_deleted_records():
    active = Widget.objects.create(name="active")
    deleted = Widget.objects.create(name="deleted")
    deleted.soft_delete()

    assert set(Widget.everything.all()) == {active, deleted}


def test_soft_delete_sets_deleted_at_and_persists():
    widget = Widget.objects.create(name="widget")
    assert widget.deleted_at is None

    widget.soft_delete()

    assert widget.deleted_at is not None
    reloaded = Widget.everything.get(pk=widget.pk)
    assert reloaded.deleted_at is not None


def test_restore_clears_deleted_at_and_reappears_in_default_manager():
    widget = Widget.objects.create(name="widget")
    widget.soft_delete()
    assert Widget.objects.count() == 0

    widget.restore()

    assert widget.deleted_at is None
    assert Widget.objects.count() == 1


def test_build_prefetches_returns_plain_string_for_non_relation_field():
    assert Widget.build_prefetches(["name"]) == ["name"]


def test_build_prefetches_returns_filtered_prefetch_for_soft_delete_relation():
    widget = Widget.objects.create(name="widget")
    Gadget.objects.create(name="gadget", widget=widget)

    prefetches = Gadget.build_prefetches(["widget"])

    assert len(prefetches) == 1
    assert isinstance(prefetches[0], Prefetch)
