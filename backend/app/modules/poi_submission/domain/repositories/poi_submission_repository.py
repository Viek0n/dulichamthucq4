from abc import ABC, abstractmethod

from app.modules.poi_submission.domain.entities.poi_submission import POISubmission


class POISubmissionRepository(ABC):
    @abstractmethod
    def create(self, submission: POISubmission) -> POISubmission:
        pass

    @abstractmethod
    def update_pending(self, submission: POISubmission) -> POISubmission:
        pass

    @abstractmethod
    def update_review(self, submission: POISubmission) -> POISubmission:
        pass

    @abstractmethod
    def get_by_id(self, submission_id: str) -> POISubmission | None:
        pass

    @abstractmethod
    def get_by_submitter(self, submitter_id: str) -> list[POISubmission]:
        pass

    @abstractmethod
    def get_all(self) -> list[POISubmission]:
        pass

    @abstractmethod
    def delete_pending(self, submission_id: str, submitter_id: str) -> bool:
        pass

    @abstractmethod
    def delete(self, submission_id: str) -> bool:
        pass
