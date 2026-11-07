from abc import ABC, abstractmethod
from app.domain.entities.poi import POI

class POIRepository(ABC):
    @abstractmethod
    def create(self, poi: POI) -> POI:
        pass

    @abstractmethod
    def update(self, poi:POI) -> POI:
        pass

    @abstractmethod
    def soft_delete(self, poi:POI) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, poi:POI) -> POI | None:
        pass

    @abstractmethod
    def get_by_slug(self, poi:POI) -> POI | None:
        pass