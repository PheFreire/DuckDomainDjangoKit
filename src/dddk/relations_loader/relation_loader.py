from typing import (
    Any,
    TypeVar,
)

from dddk.types.base_dto import (
    BaseDto,
)
from dddk.error.app_error import (
    AppError,
)
from dddk.crud.dtos.where_dto import (
    WhereDto,
)
from dddk.relations_loader.dtos.fk_relation_config import (
    FkRelationConfig,
)
from dddk.relations_loader.dtos.m2m_relation_config import (
    M2MRelationConfig,
)
from dddk.relations_loader.dtos.relation_loader_config import (
    RelationLoaderConfig,
)
from dddk.relations_loader.dtos.relation_loader_result import (
    RelationLoaderResult,
)
from dddk.relations_loader.dtos.has_many_relation_config import (
    HasManyRelationConfig,
)
from dddk.relations_loader.dtos.m2m_with_pivot_relation_config import (
    M2MWithPivotRelationConfig,
)

DTO = TypeVar("DTO", bound=BaseDto)


class RelationLoader:
    """
    Enriches lists of DTOs with their declared relations using batch queries.

    Centralizes FK, M2M and has-many relation loading so that flows remain free
    of population logic. All queries are executed in batch, avoiding N+1 problems.
    Relations to load are controlled declaratively via ``RelationLoaderConfig``
    and an ``include`` DTO — only flagged relations are fetched.
    """

    def load(
        self,
        dtos: list[DTO],
        include: BaseDto,
        config: RelationLoaderConfig,
    ) -> RelationLoaderResult[DTO]:
        """
        Enrich a list of DTOs with their declared relations.

        Iterates over FK, M2M and has-many relation configs, loading only the
        relations flagged as active in ``include``. Returns a
        ``RelationLoaderResult`` wrapping the same ``dtos`` list, mutated in place.
        """
        if not dtos:
            return RelationLoaderResult(items=dtos)

        for fk_relation in config.fk_relations:
            if self._should_include(include, fk_relation.include_field):
                self._populate_fk_relation(dtos=dtos, config=fk_relation)

        for m2m_relation in config.m2m_relations:
            if self._should_include(include, m2m_relation.include_field):
                self._populate_m2m_relation(dtos=dtos, config=m2m_relation)

        for m2m_pivot_relation in config.m2m_with_pivot_relations:
            if self._should_include(include, m2m_pivot_relation.include_field):
                self._populate_m2m_with_pivot_relation(
                    dtos=dtos, config=m2m_pivot_relation
                )

        for has_many_relation in config.has_many_relations:
            if self._should_include(include, has_many_relation.include_field):
                self._populate_has_many_relation(
                    dtos=dtos, config=has_many_relation
                )

        return RelationLoaderResult(items=dtos)

    def _should_include(self, include: BaseDto, include_field: str) -> bool:
        """Return ``True`` if ``include_field`` is truthy on the include DTO."""
        return bool(getattr(include, include_field, False))

    def _populate_fk_relation(
        self,
        dtos: list[DTO],
        config: FkRelationConfig,
    ) -> None:
        """
        Resolve a Foreign Key relation and assign the related object to each DTO.

        Collects all ``source_id_field`` values, fetches the related entities in
        a single batch query, then sets ``target_field`` on each DTO via
        ``setattr``. DTOs whose source ID is missing or not a string are skipped.
        """
        relation_ids = {
            rid
            for dto in dtos
            if isinstance(
                rid := getattr(dto, config.source_id_field, None), str
            )
            and rid
        }

        if not relation_ids:
            return

        where = self._build_where_dto(
            where_dto=config.where_dto,
            field_name=config.where_ids_field,
            value=list(relation_ids),
            context={
                "source_id_field": config.source_id_field,
                "target_field": config.target_field,
                "where_dto": config.where_dto.__name__,
            },
        )

        relations = config.repository.find(where).all
        relation_by_id = {
            getattr(relation, config.relation_id_field): relation
            for relation in relations
            if isinstance(
                getattr(relation, config.relation_id_field, None), str
            )
        }

        for dto in dtos:
            relation_id = getattr(dto, config.source_id_field, None)
            if not isinstance(relation_id, str):
                continue

            setattr(dto, config.target_field, relation_by_id.get(relation_id))

    def _populate_m2m_relation(
        self,
        dtos: list[DTO],
        config: M2MRelationConfig,
    ) -> None:
        """
        Resolve a Many-to-Many relation and assign the related list to each DTO.

        Executes two batch queries: one against the join table to map parent IDs
        to related IDs, and one against the related entity table. The results are
        grouped by parent ID and assigned to ``target_field`` on each DTO.
        Returns early if no join records or related entities are found.
        """
        parent_ids = [
            pid
            for dto in dtos
            if isinstance(
                pid := getattr(dto, config.parent_id_field, None), str
            )
        ]

        if not parent_ids:
            return

        m2m_where = self._build_where_dto(
            where_dto=config.m2m_where_dto,
            field_name=config.m2m_where_parent_ids_field,
            value=parent_ids,
            context={
                "parent_id_field": config.parent_id_field,
                "target_field": config.target_field,
                "where_dto": config.m2m_where_dto.__name__,
            },
        )

        m2m_relations = config.m2m_repository.find(m2m_where).all

        related_ids_by_parent_id: dict[str, list[str]] = {}
        related_ids: set[str] = set()

        for relation in m2m_relations:
            parent_id = getattr(relation, config.m2m_parent_id_field, None)
            related_id = getattr(relation, config.m2m_related_id_field, None)

            if not isinstance(parent_id, str) or not isinstance(
                related_id, str
            ):
                continue

            if parent_id not in related_ids_by_parent_id:
                related_ids_by_parent_id[parent_id] = []

            related_ids_by_parent_id[parent_id].append(related_id)
            related_ids.add(related_id)

        if not related_ids:
            return

        relation_where = self._build_where_dto(
            where_dto=config.relation_where_dto,
            field_name=config.relation_where_ids_field,
            value=list(related_ids),
            context={
                "target_field": config.target_field,
                "where_dto": config.relation_where_dto.__name__,
            },
        )

        related_entities = config.relation_repository.find(relation_where).all
        related_by_id = {
            getattr(related, config.relation_id_field): related
            for related in related_entities
            if isinstance(
                getattr(related, config.relation_id_field, None), str
            )
        }

        for dto in dtos:
            parent_id = getattr(dto, config.parent_id_field, None)
            if not isinstance(parent_id, str):
                continue

            dto_related_ids = related_ids_by_parent_id.get(parent_id, [])
            if not dto_related_ids:
                continue

            related_items = [
                related_by_id[related_id]
                for related_id in dto_related_ids
                if related_id in related_by_id
            ]

            setattr(dto, config.target_field, related_items)

    def _populate_has_many_relation(
        self,
        dtos: list[DTO],
        config: HasManyRelationConfig,
    ) -> None:
        """
        Resolve a has-many relation and assign the children list to each DTO.

        Executes a single batch query against the children repository filtered by
        all parent IDs at once. Children are grouped by ``child_parent_id_field``
        and assigned to ``target_field`` on the corresponding parent DTO.
        """
        parent_ids = [
            pid
            for dto in dtos
            if isinstance(
                pid := getattr(dto, config.parent_id_field, None), str
            )
        ]

        if not parent_ids:
            return

        where = self._build_where_dto(
            where_dto=config.where_dto,
            field_name=config.where_parent_ids_field,
            value=parent_ids,
            context={
                "parent_id_field": config.parent_id_field,
                "target_field": config.target_field,
                "where_dto": config.where_dto.__name__,
            },
        )

        children = config.repository.find(where).all

        children_by_parent_id: dict[str, list] = {}
        for child in children:
            parent_id = getattr(child, config.child_parent_id_field, None)
            if not isinstance(parent_id, str):
                continue
            if parent_id not in children_by_parent_id:
                children_by_parent_id[parent_id] = []
            children_by_parent_id[parent_id].append(child)

        for dto in dtos:
            parent_id = getattr(dto, config.parent_id_field, None)
            if not isinstance(parent_id, str):
                continue
            setattr(
                dto,
                config.target_field,
                children_by_parent_id.get(parent_id, []),
            )

    def _populate_m2m_with_pivot_relation(
        self,
        dtos: list[DTO],
        config: M2MWithPivotRelationConfig,
    ) -> None:
        """
        Resolve a M2M relation keeping the pivot record as the target,
        enriched with the related entity set onto it.

        Executes two batch queries: one against the pivot table to fetch
        join records (which carry extra attributes such as ``value``), and
        one against the related entity table. For each pivot record, the
        resolved related entity is assigned to ``pivot_target_field`` via
        ``setattr``. The enriched pivot records are then grouped by parent
        ID and assigned to ``target_field`` on each parent DTO.
        """
        parent_ids = [
            pid
            for dto in dtos
            if isinstance(
                pid := getattr(dto, config.parent_id_field, None), str
            )
        ]

        if not parent_ids:
            return

        pivot_where = self._build_where_dto(
            where_dto=config.pivot_where_dto,
            field_name=config.pivot_where_parent_ids_field,
            value=parent_ids,
            context={
                "parent_id_field": config.parent_id_field,
                "target_field": config.target_field,
                "where_dto": config.pivot_where_dto.__name__,
            },
        )

        pivot_records = config.pivot_repository.find(pivot_where).all
        if not pivot_records:
            for dto in dtos:
                if isinstance(getattr(dto, config.parent_id_field, None), str):
                    setattr(dto, config.target_field, [])
            return

        related_ids: set[str] = set()
        for record in pivot_records:
            related_id = getattr(record, config.pivot_related_id_field, None)
            if isinstance(related_id, str) and related_id:
                related_ids.add(related_id)

        related_by_id: dict[str, Any] = {}
        if related_ids:
            relation_where = self._build_where_dto(
                where_dto=config.relation_where_dto,
                field_name=config.relation_where_ids_field,
                value=list(related_ids),
                context={
                    "target_field": config.target_field,
                    "pivot_target_field": config.pivot_target_field,
                    "where_dto": config.relation_where_dto.__name__,
                },
            )
            related_entities = config.relation_repository.find(
                relation_where
            ).all
            related_by_id = {
                getattr(related, config.relation_id_field): related
                for related in related_entities
                if isinstance(
                    getattr(related, config.relation_id_field, None), str
                )
            }

        pivot_by_parent: dict[str, list] = {}
        for record in pivot_records:
            parent_id = getattr(record, config.pivot_parent_id_field, None)
            related_id = getattr(record, config.pivot_related_id_field, None)

            if not isinstance(parent_id, str):
                continue

            if isinstance(related_id, str) and related_id in related_by_id:
                setattr(
                    record,
                    config.pivot_target_field,
                    related_by_id[related_id],
                )

            if parent_id not in pivot_by_parent:
                pivot_by_parent[parent_id] = []
            pivot_by_parent[parent_id].append(record)

        for dto in dtos:
            parent_id = getattr(dto, config.parent_id_field, None)
            if not isinstance(parent_id, str):
                continue
            setattr(
                dto, config.target_field, pivot_by_parent.get(parent_id, [])
            )

    def _build_where_dto(
        self,
        where_dto: type[WhereDto],
        field_name: str,
        value: Any,
        context: dict[str, Any],
    ) -> WhereDto:
        """
        Instantiate a ``WhereDto`` subclass and set ``field_name`` to ``value``.

        Raises ``AppError(500)`` if ``field_name`` does not exist on the DTO,
        catching misconfigured ``RelationLoaderConfig`` declarations early.
        """
        instance = where_dto()

        if not hasattr(instance, field_name):
            raise AppError(
                "relation_loader_invalid_where_field",
                "Relation Loader Invalid Where Field",
                f'{where_dto.__name__} missing required field "{field_name}"',
                {
                    "field_name": field_name,
                    "where_dto": where_dto.__name__,
                    **context,
                },
                code=500,
            )

        setattr(instance, field_name, value)
        return instance
