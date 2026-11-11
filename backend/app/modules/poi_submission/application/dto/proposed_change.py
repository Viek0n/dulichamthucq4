from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class POIFieldChanges(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1)
    address: str | None = Field(default=None, min_length=1)
    open_at: str | None = None
    close_at: str | None = None
    contact: str | None = Field(default=None, min_length=1)
    description: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    trigger_radius: float | None = Field(default=None, ge=5, le=200)

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one POI field change is required")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("POI changes cannot contain null values")
        return self


class UpdatePOIAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["update_poi"]
    changes: POIFieldChanges


class CreateMenuItemAction(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    action: Literal["create_menu_item"]
    name: str = Field(min_length=1)
    price: int = Field(ge=1)


class UpdateMenuItemAction(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    action: Literal["update_menu_item"]
    menu_item_id: str = Field(pattern=r"^[a-fA-F0-9]{24}$")
    name: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set.intersection({"name", "price"}):
            raise ValueError("At least one menu item field change is required")
        if any(
            getattr(self, field) is None
            for field in self.model_fields_set.intersection({"name", "price"})
        ):
            raise ValueError("Menu item changes cannot contain null values")
        return self


class DeleteMenuItemAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["delete_menu_item"]
    menu_item_id: str = Field(pattern=r"^[a-fA-F0-9]{24}$")


ProposedOperation = Annotated[
    UpdatePOIAction
    | CreateMenuItemAction
    | UpdateMenuItemAction
    | DeleteMenuItemAction,
    Field(discriminator="action"),
]


class ProposedChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operations: list[ProposedOperation] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_operation_targets(self):
        updated_pois = sum(
            operation.action == "update_poi" for operation in self.operations
        )
        if updated_pois > 1:
            raise ValueError("A proposal can update the POI only once")
        return self
