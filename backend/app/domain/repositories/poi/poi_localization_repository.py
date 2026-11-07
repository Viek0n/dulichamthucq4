from abc import ABC, abstractmethod
from backend.app.domain.entities.poi.poi_localization import POILocalization

class POILocalizationRepository(ABC):
    @abstractmethod
    def create(self, poilocalization:POILocalization) -> POILocalization:
        pass

    @abstractmethod
    def update(self, poilocalization:POILocalization) -> POILocalization:
        pass

    @abstractmethod
    def delete(self, poilocalization:POILocalization) -> bool:
        pass

    @abstractmethod
    def find_by_id(self, poilocalization:POILocalization) -> POILocalization:
        pass
    