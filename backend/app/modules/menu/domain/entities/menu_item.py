from dataclasses import dataclass


@dataclass
class MenuItem:
    id: str | None
    poi_id: str
    name: str
    price: int

    def __post_init__(self):
        if not self.poi_id:
            raise ValueError("POI id is required")
        if not self.name.strip():
            raise ValueError("Menu item name is required")
        if self.price < 1:
            raise ValueError("Menu item price must be greater than zero")
