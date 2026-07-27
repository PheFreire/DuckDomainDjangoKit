from dddk import (
    Null,
    WhereDto,
    CreateDto,
    UpdateDto,
)


class _XxxCreateDto(CreateDto):
    name: str


class _XxxUpdateDto(UpdateDto):
    name: str


class _XxxWhereDto(WhereDto):
    name: str = "default"


def test_where_dto_base_fields_default_to_null():
    where = _XxxWhereDto()
    assert where.uuid == Null
    assert where.uuids == Null
    assert where.created_at == Null
    assert where.updated_at == Null
    assert where.deleted_at == Null


def test_where_dto_accepts_explicit_uuids_list():
    where = _XxxWhereDto(uuids=["a", "b"])
    assert where.uuids == ["a", "b"]


def test_create_dto_and_update_dto_are_plain_base_dtos():
    create = _XxxCreateDto(name="widget")
    update = _XxxUpdateDto(name="widget")
    assert create.name == "widget"
    assert update.name == "widget"
