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
from dddk.relations_loader.dtos import (
    FkRelationConfig,
    M2MRelationConfig,
    RelationLoaderConfig,
    HasManyRelationConfig,
    M2MWithPivotRelationConfig,
)
from dddk.crud.tools.query_response import (
    QueryResponse,
)
from dddk.relations_loader.relation_loader import (
    RelationLoader,
)


class TagDto(BaseDto):
    uuid: str
    name: str


class TagWhereDto(WhereDto):
    pass


class RespondentTagDto(BaseDto):
    respondent_id: str
    tag_id: str
    tag: TagDto | None = None


class RespondentTagWhereDto(WhereDto):
    respondent_ids: NullOr[list[str]] = Null


class AnswerDto(BaseDto):
    uuid: str
    respondent_id: str | None = None
    respondent: Any = None


class AnswerWhereDto(WhereDto):
    respondent_ids: NullOr[list[str]] = Null


class RespondentDto(BaseDto):
    uuid: str
    name: str
    answers: list[AnswerDto] | None = None
    tags: list[TagDto] | None = None
    respondent_tags: list[RespondentTagDto] | None = None


class RespondentWhereDto(WhereDto):
    pass


class IncludeDto(BaseDto):
    respondent: bool = False
    answers: bool = False
    tags: bool = False
    respondent_tags: bool = False


class _FakeRepository:
    def __init__(self, data: list):
        self.data = data
        self.calls: list = []

    def find(self, where):
        self.calls.append(where)
        return QueryResponse(self.data, "fake")


def test_load_with_empty_dtos_returns_immediately_without_querying():
    repository = _FakeRepository([RespondentDto(uuid="r1", name="Alice")])
    loader = RelationLoader()

    result = loader.load(
        dtos=[],
        include=IncludeDto(respondent=True),
        config=RelationLoaderConfig(
            fk_relations=[
                FkRelationConfig(
                    include_field="respondent",
                    source_id_field="respondent_id",
                    target_field="respondent",
                    repository=repository,
                    where_dto=RespondentWhereDto,
                    where_ids_field="uuids",
                )
            ]
        ),
    )

    assert result.items == []
    assert repository.calls == []


def test_fk_relation_populates_target_field():
    answers = [
        AnswerDto(uuid="a1", respondent_id="r1"),
        AnswerDto(uuid="a2", respondent_id="r2"),
        AnswerDto(uuid="a3", respondent_id=None),
    ]
    respondents = [RespondentDto(uuid="r1", name="Alice")]
    repository = _FakeRepository(respondents)

    result = RelationLoader().load(
        dtos=answers,
        include=IncludeDto(respondent=True),
        config=RelationLoaderConfig(
            fk_relations=[
                FkRelationConfig(
                    include_field="respondent",
                    source_id_field="respondent_id",
                    target_field="respondent",
                    repository=repository,
                    where_dto=RespondentWhereDto,
                    where_ids_field="uuids",
                )
            ]
        ),
    )

    assert result.items[0].respondent.uuid == "r1"
    assert result.items[1].respondent is None  # r2 not found in repository
    assert result.items[2].respondent is None  # no respondent_id at all


def test_fk_relation_is_skipped_when_include_flag_is_false():
    answers = [AnswerDto(uuid="a1", respondent_id="r1")]
    repository = _FakeRepository([RespondentDto(uuid="r1", name="Alice")])

    result = RelationLoader().load(
        dtos=answers,
        include=IncludeDto(respondent=False),
        config=RelationLoaderConfig(
            fk_relations=[
                FkRelationConfig(
                    include_field="respondent",
                    source_id_field="respondent_id",
                    target_field="respondent",
                    repository=repository,
                    where_dto=RespondentWhereDto,
                    where_ids_field="uuids",
                )
            ]
        ),
    )

    assert result.items[0].respondent is None
    assert repository.calls == []


def test_has_many_relation_groups_children_by_parent():
    respondents = [
        RespondentDto(uuid="r1", name="Alice"),
        RespondentDto(uuid="r2", name="Bob"),
    ]
    answers = [
        AnswerDto(uuid="a1", respondent_id="r1"),
        AnswerDto(uuid="a2", respondent_id="r1"),
        AnswerDto(uuid="a3", respondent_id="r2"),
    ]
    repository = _FakeRepository(answers)

    result = RelationLoader().load(
        dtos=respondents,
        include=IncludeDto(answers=True),
        config=RelationLoaderConfig(
            has_many_relations=[
                HasManyRelationConfig(
                    include_field="answers",
                    parent_id_field="uuid",
                    target_field="answers",
                    child_parent_id_field="respondent_id",
                    repository=repository,
                    where_dto=AnswerWhereDto,
                    where_parent_ids_field="respondent_ids",
                )
            ]
        ),
    )

    by_uuid = {r.uuid: r for r in result.items}
    assert {a.uuid for a in by_uuid["r1"].answers} == {"a1", "a2"}
    assert {a.uuid for a in by_uuid["r2"].answers} == {"a3"}
    assert repository.calls[0].respondent_ids == ["r1", "r2"]


def test_m2m_relation_resolves_related_entities_through_join_table():
    respondents = [RespondentDto(uuid="r1", name="Alice")]
    join_rows = [RespondentTagDto(respondent_id="r1", tag_id="t1")]
    tags = [TagDto(uuid="t1", name="vip")]

    join_repository = _FakeRepository(join_rows)
    tag_repository = _FakeRepository(tags)

    result = RelationLoader().load(
        dtos=respondents,
        include=IncludeDto(tags=True),
        config=RelationLoaderConfig(
            m2m_relations=[
                M2MRelationConfig(
                    include_field="tags",
                    parent_id_field="uuid",
                    target_field="tags",
                    m2m_repository=join_repository,
                    m2m_where_dto=RespondentTagWhereDto,
                    m2m_where_parent_ids_field="respondent_ids",
                    m2m_parent_id_field="respondent_id",
                    m2m_related_id_field="tag_id",
                    relation_id_field="uuid",
                    relation_repository=tag_repository,
                    relation_where_dto=TagWhereDto,
                    relation_where_ids_field="uuids",
                )
            ]
        ),
    )

    assert [t.name for t in result.items[0].tags] == ["vip"]


def test_m2m_relation_returns_early_when_no_join_records_found():
    respondents = [RespondentDto(uuid="r1", name="Alice")]
    join_repository = _FakeRepository([])
    tag_repository = _FakeRepository([TagDto(uuid="t1", name="vip")])

    RelationLoader().load(
        dtos=respondents,
        include=IncludeDto(tags=True),
        config=RelationLoaderConfig(
            m2m_relations=[
                M2MRelationConfig(
                    include_field="tags",
                    parent_id_field="uuid",
                    target_field="tags",
                    m2m_repository=join_repository,
                    m2m_where_dto=RespondentTagWhereDto,
                    m2m_where_parent_ids_field="respondent_ids",
                    m2m_parent_id_field="respondent_id",
                    m2m_related_id_field="tag_id",
                    relation_id_field="uuid",
                    relation_repository=tag_repository,
                    relation_where_dto=TagWhereDto,
                    relation_where_ids_field="uuids",
                )
            ]
        ),
    )

    assert tag_repository.calls == []


def test_m2m_with_pivot_relation_enriches_pivot_record_and_groups_by_parent():
    respondents = [RespondentDto(uuid="r1", name="Alice")]
    join_rows = [RespondentTagDto(respondent_id="r1", tag_id="t1")]
    tags = [TagDto(uuid="t1", name="vip")]

    join_repository = _FakeRepository(join_rows)
    tag_repository = _FakeRepository(tags)

    result = RelationLoader().load(
        dtos=respondents,
        include=IncludeDto(respondent_tags=True),
        config=RelationLoaderConfig(
            m2m_with_pivot_relations=[
                M2MWithPivotRelationConfig(
                    include_field="respondent_tags",
                    parent_id_field="uuid",
                    target_field="respondent_tags",
                    pivot_repository=join_repository,
                    pivot_where_dto=RespondentTagWhereDto,
                    pivot_where_parent_ids_field="respondent_ids",
                    pivot_parent_id_field="respondent_id",
                    pivot_related_id_field="tag_id",
                    pivot_target_field="tag",
                    relation_repository=tag_repository,
                    relation_where_dto=TagWhereDto,
                    relation_where_ids_field="uuids",
                    relation_id_field="uuid",
                )
            ]
        ),
    )

    pivot = result.items[0].respondent_tags[0]
    assert pivot.tag_id == "t1"
    assert pivot.tag.name == "vip"


def test_m2m_with_pivot_relation_assigns_empty_list_when_no_pivot_records():
    respondents = [RespondentDto(uuid="r1", name="Alice")]
    join_repository = _FakeRepository([])
    tag_repository = _FakeRepository([])

    result = RelationLoader().load(
        dtos=respondents,
        include=IncludeDto(respondent_tags=True),
        config=RelationLoaderConfig(
            m2m_with_pivot_relations=[
                M2MWithPivotRelationConfig(
                    include_field="respondent_tags",
                    parent_id_field="uuid",
                    target_field="respondent_tags",
                    pivot_repository=join_repository,
                    pivot_where_dto=RespondentTagWhereDto,
                    pivot_where_parent_ids_field="respondent_ids",
                    pivot_parent_id_field="respondent_id",
                    pivot_related_id_field="tag_id",
                    pivot_target_field="tag",
                    relation_repository=tag_repository,
                    relation_where_dto=TagWhereDto,
                    relation_where_ids_field="uuids",
                    relation_id_field="uuid",
                )
            ]
        ),
    )

    assert result.items[0].respondent_tags == []


def test_build_where_dto_raises_app_error_for_unknown_field():
    answers = [AnswerDto(uuid="a1", respondent_id="r1")]
    repository = _FakeRepository([])

    with pytest.raises(AppError) as exc_info:
        RelationLoader().load(
            dtos=answers,
            include=IncludeDto(respondent=True),
            config=RelationLoaderConfig(
                fk_relations=[
                    FkRelationConfig(
                        include_field="respondent",
                        source_id_field="respondent_id",
                        target_field="respondent",
                        repository=repository,
                        where_dto=RespondentWhereDto,
                        where_ids_field="this_field_does_not_exist",
                    )
                ]
            ),
        )

    assert exc_info.value.code == 500
