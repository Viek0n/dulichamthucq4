from dataclasses import dataclass
from app.domain.constants.default import TRIGGER_RADIUS

@dataclass
class POI:
    _id: str
    slug: str
    name: str
    address: str
    open_at: str
    close_at: str
    contact: str
    imgae: str
    latitude: float
    longitude: float
    trigger_radius: float = TRIGGER_RADIUS
    is_delete: bool = False
    poi_owner_id: str = ""

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError("Kinh độ không hợp lệ")

        if not -180 <= self.longitude <= 180:
            raise ValueError("Vĩ độ không hợp lệ")

        if not 5 <= self.trigger_radius <= 200:
            raise ValueError("Khoảng cách kích hoạt không hợp lệ")