from pydantic import BaseModel

class POIResponse(BaseModel):
    slug: str
    name: str
    address: str
    open_at: str
    close_at: str
    contact: str
    image: str
    latitude: float
    longitude: float
    trigger_radius: float
    poi_owner: str