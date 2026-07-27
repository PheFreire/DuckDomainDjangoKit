from typing import (
    Any,
)

import pytest

from dddk import (
    Null,
    NullOr,
    BaseDto,
    AppError,
    WhereDto,
)
from dddk.crud.tools.query_response import (
    QueryResponse,
)
from dddk.crud.tools.populate_fk_relations import (
    populate_fk_relations,
)


class RegionDto(BaseDto):
    id: str
    name: str


class RegionWhereDto(WhereDto):
    ids: NullOr[list[str]] = Null


class RegionlessWhereDto(WhereDto):
    """A WhereDto that does not expose an ``ids`` field."""


class CityDto(BaseDto):
    uuid: str
    region: Any = None


class _FakeRepository:
    def __init__(self, data: list):
        self.data = data
        self.calls: list = []

    def find(self, where):
        self.calls.append(where)
        return QueryResponse(self.data, "fake")


def test_populates_matching_region_by_id():
    cities = [CityDto(uuid="c1", region="r1"), CityDto(uuid="c2", region="r2")]
    repository = _FakeRepository([RegionDto(id="r1", name="North")])

    result = populate_fk_relations(
        cities, "region", repository, RegionWhereDto
    )

    assert result[0].region.name == "North"
    assert result[1].region is None
    assert sorted(repository.calls[0].ids) == ["r1", "r2"]


def test_returns_dtos_unchanged_when_no_relation_ids_present():
    cities = [CityDto(uuid="c1", region=None)]
    repository = _FakeRepository([])

    result = populate_fk_relations(
        cities, "region", repository, RegionWhereDto
    )

    assert result[0].region is None
    assert repository.calls == []


def test_raises_app_error_when_where_dto_has_no_ids_field():
    cities = [CityDto(uuid="c1", region="r1")]
    repository = _FakeRepository([])

    with pytest.raises(AppError) as exc_info:
        populate_fk_relations(cities, "region", repository, RegionlessWhereDto)

    assert exc_info.value.code == 500
