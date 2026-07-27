from dddk.types.base_dto import (
    BaseDto,
)


class UpdateDto(BaseDto):
    """
    Base Data Transfer Object (DTO) for entity update operations.

    This class defines the structure for updating existing domain entities.
    It ensures that all subclass fields are compatible with `NullOr` types,
    allowing partial updates (i.e., fields can be omitted or explicitly set
    to `Null` to represent no change).

    During subclass creation, the `validate_null_or_field` validator checks
    that every declared field supports nullable or optional values, enforcing
    the correct update semantics at class definition time.

    Example
    -------
        class ResearchUpdateDto(UpdateDto):
            title: NullOr[str]
            description: NullOr[str]

        # Example usage:
        payload = ResearchUpdateDto(title="New Title")
        # Only the 'title' field will be updated.

    Notes
    -----
    - `UpdateDto` provides a strict contract for partial updates: every field
      must either be nullable (`NullOr[T]`) or optional.
    - Validation occurs automatically when a subclass is defined, ensuring
      that DTOs used for update operations are consistent with domain rules.

    Raises
    ------
    TypeError
        If any subclass field does not support `NullOr` typing.
    """
