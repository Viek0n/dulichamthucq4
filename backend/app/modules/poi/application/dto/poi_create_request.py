from pydantic import BaseModel, Field, ConfigDict

from app.modules.poi.domain.constants.parameters import TRIGGER_RADIUS


class POICreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)

    open_at: str
    close_at: str

    contact: str = Field(min_length=1)
    description: str = ""
    image: str = ""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    trigger_radius: float = Field(
        default=TRIGGER_RADIUS,
        ge=5,
        le=200
    )