from dataclasses import dataclass
from app.domain.enumerators.language import Language

@dataclass
class POILocalization():
    id: str
    poi_id: str
    lang: Language
    menu: str