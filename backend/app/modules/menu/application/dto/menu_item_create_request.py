from pydantic import BaseModel, Field

class MenuItemCreateRequest(BaseModel):
    poi_id: str
    name: str
    price: int = Field(ge=1)