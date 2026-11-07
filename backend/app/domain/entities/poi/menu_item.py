from dataclasses import dataclass

@dataclass
class MenuItem:
    _id: str
    poi_id: str
    name: str
    price: int