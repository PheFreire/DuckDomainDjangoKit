from dddk import (
    Null,
    NullOr,
    BaseDto,
    WhereDto,
)
from dddk.crud.tools.query_response import (
    QueryResponse,
)
from dddk.crud.tools.populate_m2m_relations import (
    populate_m2m_relations,
)


class BookDto(BaseDto):
    id: str
    title: str


class BookWhereDto(WhereDto):
    ids: NullOr[list[str]] = Null


class AuthorBookDto(BaseDto):
    author_id: str
    book_id: str


class AuthorBookWhereDto(WhereDto):
    author_ids: NullOr[list[str]] = Null


class AuthorDto(BaseDto):
    id: str
    books: list[BookDto] | None = None


class _FakeRepository:
    def __init__(self, data: list):
        self.data = data
        self.calls: list = []

    def find(self, where):
        self.calls.append(where)
        return QueryResponse(self.data, "fake")


def test_populates_related_entities_grouped_by_parent():
    authors = [AuthorDto(id="a1"), AuthorDto(id="a2")]
    join_repository = _FakeRepository(
        [AuthorBookDto(author_id="a1", book_id="b1")]
    )
    book_repository = _FakeRepository([BookDto(id="b1", title="Dune")])

    result = populate_m2m_relations(
        dtos=authors,
        dto_relation_field="books",
        m2m_repository=join_repository,
        m2m_where=AuthorBookWhereDto,
        m2m_where_parent_ids_field="author_ids",
        m2m_parent_id_field="author_id",
        m2m_related_id_field="book_id",
        relation_repository=book_repository,
        relation_where=BookWhereDto,
    )

    by_id = {a.id: a for a in result}
    assert [b.title for b in by_id["a1"].books] == ["Dune"]
    assert by_id["a2"].books is None
    assert join_repository.calls[0].author_ids == ["a1", "a2"]


def test_extends_existing_relation_list_instead_of_overwriting():
    author = AuthorDto(id="a1", books=[BookDto(id="b0", title="Existing")])
    join_repository = _FakeRepository(
        [AuthorBookDto(author_id="a1", book_id="b1")]
    )
    book_repository = _FakeRepository([BookDto(id="b1", title="Dune")])

    result = populate_m2m_relations(
        dtos=[author],
        dto_relation_field="books",
        m2m_repository=join_repository,
        m2m_where=AuthorBookWhereDto,
        m2m_where_parent_ids_field="author_ids",
        m2m_parent_id_field="author_id",
        m2m_related_id_field="book_id",
        relation_repository=book_repository,
        relation_where=BookWhereDto,
    )

    assert [b.title for b in result[0].books] == ["Existing", "Dune"]


def test_returns_dtos_unchanged_when_no_dtos_given():
    assert (
        populate_m2m_relations(
            dtos=[],
            dto_relation_field="books",
            m2m_repository=_FakeRepository([]),
            m2m_where=AuthorBookWhereDto,
            m2m_where_parent_ids_field="author_ids",
            m2m_parent_id_field="author_id",
            m2m_related_id_field="book_id",
            relation_repository=_FakeRepository([]),
            relation_where=BookWhereDto,
        )
        == []
    )


def test_returns_dtos_unchanged_when_no_join_records_found():
    authors = [AuthorDto(id="a1")]
    join_repository = _FakeRepository([])
    book_repository = _FakeRepository([BookDto(id="b1", title="Dune")])

    result = populate_m2m_relations(
        dtos=authors,
        dto_relation_field="books",
        m2m_repository=join_repository,
        m2m_where=AuthorBookWhereDto,
        m2m_where_parent_ids_field="author_ids",
        m2m_parent_id_field="author_id",
        m2m_related_id_field="book_id",
        relation_repository=book_repository,
        relation_where=BookWhereDto,
    )

    assert result[0].books is None
    assert book_repository.calls == []
