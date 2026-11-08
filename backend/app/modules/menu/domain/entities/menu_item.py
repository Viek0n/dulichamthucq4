from dataclasses import dataclass

@dataclass
class MenuItem:
    id: str
    poi_id: str
    name: str
    price: int