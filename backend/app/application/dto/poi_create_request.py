from pydantic import BaseModel, Field
from app.domain.constants.default import TRIGGER_RADIUS

class POICreateRequest(BaseModel):
    slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    address: str
    open_at: str
    close_at: str
    contact: str
    image: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    trigger_radius: float = Field(
        default = TRIGGER_RADIUS,
        ge=5,
        le=200
    )