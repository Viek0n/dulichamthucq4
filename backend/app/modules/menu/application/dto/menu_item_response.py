from pydantic import BaseModel


class MenuItemResponse(BaseModel):
    id: str
    poi_id: str
    name: str
    price: int
