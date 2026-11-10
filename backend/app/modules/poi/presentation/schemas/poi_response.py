from pydantic import BaseModel


class POIResponse(BaseModel):
    id: str
    name: str
    address: str
    open_at: str
    close_at: str
    contact: str
    description: str
    image: str
    latitude: float
    longitude: float
    trigger_radius: float
    is_delete: bool = False
    poi_owner_id: str
