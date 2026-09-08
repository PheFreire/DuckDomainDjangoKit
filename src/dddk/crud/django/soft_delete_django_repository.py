from typing import (
    Generic,
    TypeVar,
    ClassVar,
    cast,
)
from functools import (
    cached_property,
)

from dddk.types.null import (
    Null,
)
from dddk.types.base_dto import (
    BaseDto,
)
from dddk.error.app_error import (
    AppError,
)
from dddk.crud.i_repository import (
    IRepository,
)
from dddk.crud.dtos.where_dto import (
    WhereDto,
)
from dddk.crud.dtos.create_dto import (
    CreateDto,
)
from dddk.crud.dtos.update_dto import (
    UpdateDto,
)
from dddk.crud.tools.query_response import (
    QueryResponse,
)
from dddk.crud.django.soft_delete_model import (
    SoftDeleteModel,
)

MODEL = TypeVar("MODEL", bound=SoftDeleteModel)
DTO = TypeVar("DTO", bound=BaseDto)
WHERE = TypeVar("WHERE", bound=WhereDto)
CREATE = TypeVar("CREATE", bound=CreateDto)
UPDATE = TypeVar("UPDATE", bound=UpdateDto)
RESPONSE = TypeVar("RESPONSE", bound=BaseDto)


class SoftDeleteDjangoRepository(
    IRepository,
    Generic[MODEL, DTO, WHERE, CREATE, UPDATE, RESPONSE],
):
    """
    A generic Django repository implementation that supports soft-delete semantics
    and integrates with Pydantic DTOs for type-safe data mapping.

    This class provides a reusable data-access layer for Django models that inherit
    from `SoftDeleteModel`, automatically handling conversions between ORM entities
    and Pydantic-based DTOs (`BaseDto`). It supports standard CRUD operations.

    Type Parameters:
        MODEL (SoftDeleteModel): The Django model class managed by this repository.
        DTO (BaseDto): The main data transfer object (domain-level representation).
        WHERE (WhereDto): DTO defining filtering criteria for queries.
        CREATE (CreateDto): DTO used for creating new records.
        UPDATE (UpdateDto): DTO used for updating existing records.
        RESPONSE (BaseDto): DTO returned in query responses.

    Attributes:
        response (Type[RESPONSE]): Class of the DTO returned in query responses.
        model (Type[SoftDeleteModel]): The Django model managed by the repository.
        dto (Type[DTO]): Class of the DTO representing the entity.
        where_field_to_filter (Dict[str, str]): Mapping between field names in the
            `WHERE` DTO and Django ORM filter expressions.
        select_related_fields (tuple[str, ...]): FK field names that `as_dto()`
            dereferences (e.g. through `get_if_active`) and that should be joined
            via `select_related` in `find()`, `create_many()` and `update()`,
            avoiding a query per row/per FK.
    """

    response: type[RESPONSE]
    model: type[SoftDeleteModel]
    dto: type[DTO]

    where_field_to_filter: ClassVar[dict[str, str]] = {}
    select_related_fields: ClassVar[tuple[str, ...]] = ()

    @cached_property
    def _model_fields(self) -> set[str]:
        """
        Cached list of model field names for fast access and filtering.

        Returns:
            List[str]: A list of field names defined in the Django model.
        """
        # `_meta.fields`
        return {f.name for f in self.model._meta.concrete_fields}

    def _as_django_filter(self, field: str) -> str:
        """
        Convert a `WHERE` DTO field name into a Django ORM filter key.

        Args:
            field (str): Field name from the `WHERE` DTO.

        Returns:
            str: Django ORM-compatible filter string.
        """
        if field in self.where_field_to_filter.keys():
            return self.where_field_to_filter[field]
        return field

    def create(self, create: CREATE) -> DTO:
        """
        Create a new record in the database from the given `CREATE` DTO.

        Args:
            create (CREATE): DTO containing field values for the new record.

        Returns:
            DTO: A Pydantic DTO representing the newly created entity.
        """
        created = self.model.objects.create(**create.model_dump())
        return cast(DTO, created.as_dto())

    def create_many(self, creates: list[CREATE]) -> QueryResponse[DTO, None]:
        """
        Create many records in the database from the given `CREATE` DTOs.

        The instances `bulk_create` returns only carry the scalar columns
        that were written (including `*_id` FK columns), never the related
        objects themselves. If `select_related_fields` is set, `as_dto()`
        dereferencing one of those FKs (e.g. through `get_if_active`) would
        otherwise fire one extra query per row per FK; this re-fetches the
        created rows in a single `select_related` query first, the same way
        `find()` already does, to avoid that.

        Args:
            creates (list[CREATE]): DTOs containing field values for the new
                records.

        Returns:
            QueryResponse[DTO, None]: The newly created entities as DTOs.
        """
        if not creates:
            return QueryResponse([], self.model._meta.db_table)

        instances = [self.model(**create.model_dump()) for create in creates]

        self.model.objects.bulk_create(instances, batch_size=500)

        if not self.select_related_fields:
            return QueryResponse(
                [cast(DTO, instance.as_dto()) for instance in instances],
                self.model._meta.db_table,
            )

        pk_field = self.model._meta.pk.name
        pks = [getattr(instance, pk_field) for instance in instances]
        by_pk = {
            getattr(obj, pk_field): obj
            for obj in self.model.objects.filter(
                **{f"{pk_field}__in": pks}
            ).select_related(*self.select_related_fields)
        }

        return QueryResponse(
            [cast(DTO, by_pk[pk].as_dto()) for pk in pks],
            self.model._meta.db_table,
        )

    def find(self, where: WHERE) -> QueryResponse[RESPONSE, WHERE]:
        where_dict = where.model_dump(
            exclude_defaults=False, exclude_none=False
        )

        ids = where_dict.pop("uuids", Null)
        if ids == Null:
            ids = where_dict.pop("ids", Null)

        if ids != Null:
            if len(ids) == 0:
                return QueryResponse([], self.model._meta.db_table, where)

            pk_field = self.model._meta.pk.name
            where_dict[f"{pk_field}__in"] = ids

        filters = {
            self._as_django_filter(field): value
            for field, value in where_dict.items()
            if value != Null
            and (
                field in self._model_fields
                or field in self.where_field_to_filter.keys()
                or (
                    field.endswith("_id")
                    and field.removesuffix("_id") in self._model_fields
                )
                or (
                    field.endswith("__in")
                    and field.removesuffix("__in") in self._model_fields
                )
            )
        }

        queryset = self.model.objects.filter(**filters)
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        result = [
            self.response(**model.as_dto().model_dump()) for model in queryset
        ]

        return QueryResponse(result, self.model._meta.db_table, where)

    def update(self, id: str, update: UPDATE) -> DTO:
        """
        Update an existing record identified by its id using data from the
        provided `UPDATE` DTO. Fields set to `Null` are ignored.

        The instance fetched here only carries its scalar columns (including
        `*_id` FK columns), never the related objects. If
        `select_related_fields` is set, `as_dto()` dereferencing one of those
        FKs (e.g. through `get_if_active`) would otherwise fire one extra
        query per FK; this re-fetches the saved row in a single
        `select_related` query first, the same way `find()` and
        `create_many()` do, to avoid that (and to return fresh related data
        when the update itself changed one of those FKs).

        Args:
            id (str): The unique identifier (id) of the record to update.
            update (UPDATE): DTO specifying the new field values.

        Returns:
            DTO: A Pydantic DTO representing the updated entity.

        Raises:
            AppError: If no record is found with the provided id.
        """
        instance = self.model.objects.filter(pk=id).first()
        if instance is None:
            self.__error(self, id)

        for field, value in update.model_dump(exclude_defaults=True).items():
            if value == Null:
                continue

            if hasattr(instance, field):
                setattr(instance, field, value)

            elif field.endswith("_id"):
                fk_field = field.removesuffix("_id")
                if hasattr(instance, fk_field):
                    setattr(instance, f"{fk_field}_id", value)

        assert instance is not None
        instance.save()

        if not self.select_related_fields:
            return cast(DTO, instance.as_dto())

        saved = (
            self.model.objects.filter(pk=id)
            .select_related(*self.select_related_fields)
            .first()
        )
        assert saved is not None
        return cast(DTO, saved.as_dto())

    def delete(self, id: str) -> str:
        """
        Perform a soft-delete operation on the record identified by its id.
        The record remains in the database but is excluded from normal queries.

        Args:
            id (str): The unique identifier (id) of the record to soft-delete.

        Returns:
            str: The id of the deleted record.

        Raises:
            AppError: If the record does not exist.
        """
        data = self.model.objects.filter(pk=id).first()

        if data is None:
            self.__error(self, id)

        assert data is not None
        data.soft_delete()
        return id

    def __error(self, cls: object, id: str):
        """
        Raise a standardized application error when a record is not found.

        Args:
            cls (object): The class or context in which the error occurred.
            id (str): The id of the missing record.

        Raises:
            AppError: With message "Not Found Error" and a 404 HTTP code.
        """
        raise AppError(
            cls,
            "Not Found Error",
            f"{self.model._meta.db_table} row not found",
            {"id": id},
            code=404,
        )
