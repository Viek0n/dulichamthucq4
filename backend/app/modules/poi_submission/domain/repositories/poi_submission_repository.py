from abc import ABC, abstractmethod
from domain.entities.poi_submission import POISubmission

class POISubmissionRepository(ABC):
    @abstractmethod
    def create(self, poi_submission: POISubmission) -> POISubmission:
        pass

    @abstractmethod
    def update(self, poi_submission:POISubmission) -> POISubmission:
        pass

    @abstractmethod
    def soft_delete(self, poi_submission:POISubmission) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, poi_submission:POISubmission) -> POISubmission | None:
        pass

    @abstractmethod
    def get_by_slug(self, poi_submission:POISubmission) -> POISubmission | None:
        pass