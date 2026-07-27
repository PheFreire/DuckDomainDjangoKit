class _TypeNull:
    """
    Sentinel type representing an explicit null value in the domain layer.

    Unlike Python's built-in `None`, this custom `Null` object is used to
    distinguish between:
      - a field intentionally set to "no value" (`Null`), and
      - a field simply omitted from input data (`None`).

    This distinction allows domain objects and DTOs to express three distinct
    states:
      1. **Value present** – field has a concrete value.
      2. **Null (explicit)** – field is intentionally set to `Null`.
      3. **Missing (implicit)** – field was not provided at all.

    `Null` integrates with the `NullOr[T]` type and is automatically serialized
    to `None` when exporting DTOs to JSON, preserving clean API compatibility
    while retaining semantic precision internally.

    Example
    -------
        from dddk.types.null import Null
        from dddk.types.null_or import NullOr

        class UserDto(BaseDto):
            name: NullOr[str] = Null

        user = UserDto(name=Null)
        assert user.name == Null  # explicit null, not None

        print(user.model_dump_json())  # {"name": null}

    Notes
    -----
    - Use `Null` instead of `None` when you want to signal that a value was
      explicitly cleared or intentionally left empty.
    - This pattern is particularly useful for partial updates and domain-driven
      data flows where absence and explicit null have distinct meanings.
    """

    __slots__ = ()

    def __str__(self) -> str:
        return "null"

    def __repr__(self) -> str:
        return "Null"

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _TypeNull)


Null = _TypeNull()
