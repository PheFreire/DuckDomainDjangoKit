from datetime import (
    datetime,
)

from pydantic import (
    Field,
)

from dddk import (
    Null,
    NullOr,
    BaseDto,
    WhereDto,
    CreateDto,
    UpdateDto,
)


class WidgetDto(BaseDto):
    uuid: str
    name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class WidgetCreateDto(CreateDto):
    name: str


class WidgetUpdateDto(UpdateDto):
    name: NullOr[str] = Field(default=Null)


class WidgetWhereDto(WhereDto):
    name: NullOr[str] = Field(default=Null)


class GadgetDto(BaseDto):
    uuid: str
    name: str
    widget_id: str
    owner_id: str | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class GadgetCreateDto(CreateDto):
    name: str
    widget_id: str
    owner_id: str | None = None


class GadgetUpdateDto(UpdateDto):
    name: NullOr[str] = Field(default=Null)
    widget_id: NullOr[str] = Field(default=Null)


class GadgetWhereDto(WhereDto):
    name: NullOr[str] = Field(default=Null)
    widget_id: NullOr[str] = Field(default=Null)
    widget_name: NullOr[str] = Field(default=Null)
