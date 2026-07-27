from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from collections.abc import (
    Sequence,
)

from dddk.relations_loader.dtos.fk_relation_config import (
    FkRelationConfig,
)
from dddk.relations_loader.dtos.m2m_relation_config import (
    M2MRelationConfig,
)
from dddk.relations_loader.dtos.has_many_relation_config import (
    HasManyRelationConfig,
)
from dddk.relations_loader.dtos.m2m_with_pivot_relation_config import (
    M2MWithPivotRelationConfig,
)


@dataclass(frozen=True)
class RelationLoaderConfig:
    """
    Declarative configuration passed to ``RelationLoader.load()``.

    Groups all relation configs by kind.  ``RelationLoader`` iterates each
    sequence in order and skips any config whose ``include_field`` is falsy
    on the ``include`` DTO provided at call time.

    Only populate the sequences you need — unused sequences default to empty
    tuples and incur no overhead.

    Attributes:
    -----------
    `fk_relations`:
        Foreign Key `(many-to-one)` relations.
        Each parent holds a scalar ID pointing to one related entity.
        See `FkRelationConfig`.

    `m2m_relations`:
        Many to Many` relations resolved through a join table
        Where only the related entities (not the join records) are assigned to the parent.
        See `M2MRelationConfig`.

    `m2m_with_pivot_relations`:
        `Many to Many` relations where the join/pivot record itself is the target enriched with the resolved related entity.
        Use when the join table carries extra attributes.
        See `M2MWithPivotRelationConfig`.

    `has_many_relations`:
        `One-to-many` relations where children reference the parent via a FK column.
        A single batch query retrieves and groups them.
        See `HasManyRelationConfig`.
    """

    fk_relations: Sequence[FkRelationConfig] = ()
    m2m_relations: Sequence[M2MRelationConfig] = ()
    m2m_with_pivot_relations: Sequence[M2MWithPivotRelationConfig] = ()
    has_many_relations: Sequence[HasManyRelationConfig] = ()
