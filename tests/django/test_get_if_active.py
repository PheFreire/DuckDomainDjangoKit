import pytest

from tests.testapp.models import (
    Widget,
)
from dddk.crud.django.utils.get_if_active import (
    get_if_active,
)

pytestmark = pytest.mark.django_db


def test_returns_uuid_string_when_not_deleted():
    widget = Widget.objects.create(name="widget")
    assert get_if_active(widget) == str(widget.uuid)


def test_returns_none_when_soft_deleted():
    widget = Widget.objects.create(name="widget")
    widget.soft_delete()
    assert get_if_active(widget) is None
