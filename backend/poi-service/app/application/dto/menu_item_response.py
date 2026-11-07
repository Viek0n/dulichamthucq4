from pydantic import BaseModel

class MenuItemResponse(BaseModel):
    poi_id: str
    name: str
    price: int