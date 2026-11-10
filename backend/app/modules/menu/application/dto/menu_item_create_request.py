from pydantic import BaseModel, Field


class MenuItemCreateRequest(BaseModel):
    poi_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    price: int = Field(ge=1)
