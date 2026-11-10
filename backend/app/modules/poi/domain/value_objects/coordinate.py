from dataclasses import dataclass
from app.modules.poi.domain.exceptions.poi_exceptions import InvalidLatitude, InvalidLongitude

@dataclass
class Coordinate:
    latitude: float
    longitude: float

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise InvalidLatitude("Vĩ độ không hợp lệ")

        if not -180 <= self.longitude <= 180:
            raise InvalidLongitude("Kinh độ không hợp lệ")