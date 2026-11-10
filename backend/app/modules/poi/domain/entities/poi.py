from dataclasses import dataclass
from app.modules.poi.domain.constants.parameters import TRIGGER_RADIUS
from app.modules.poi.domain.value_objects.coordinate import Coordinate
from app.modules.poi.domain.value_objects.at_time import AtTime

@dataclass
class POI:
    id: str
    slug: str
    name: str
    address: str
    open_at: AtTime
    close_at: AtTime
    contact: str
    description: str
    image: str
    position: Coordinate
    trigger_radius: float = TRIGGER_RADIUS
    is_delete: bool = False
    poi_owner_id: str = ""

    def __post_init__(self):
        if not -90 <= self.position.latitude <= 90:
            raise ValueError("Kinh độ không hợp lệ")

        if not -180 <= self.position.longitude <= 180:
            raise ValueError("Vĩ độ không hợp lệ")

        if not 5 <= self.trigger_radius <= 200:
            raise ValueError("Khoảng cách kích hoạt không hợp lệ")