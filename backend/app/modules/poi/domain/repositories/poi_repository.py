from abc import ABC, abstractmethod

from app.modules.poi.domain.entities.poi import POI


class POIRepository(ABC):
    @abstractmethod
    def create(self, poi: POI) -> POI:
        pass

    @abstractmethod
    def update(self, poi: POI) -> POI:
        pass

    @abstractmethod
    def soft_delete(self, poi_id: str) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, poi_id: str) -> POI | None:
        pass

    @abstractmethod
    def get_all(self) -> list[POI]:
        pass
