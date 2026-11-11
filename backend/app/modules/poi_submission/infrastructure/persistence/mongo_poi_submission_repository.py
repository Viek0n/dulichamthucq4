from datetime import datetime, timezone

from bson import ObjectId
from pymongo.collection import Collection

from app.modules.poi_submission.domain.entities.poi_submission import POISubmission
from app.modules.poi_submission.domain.enumerators.review_status import ReviewStatus
from app.modules.poi_submission.domain.exceptions.poi_submission_exceptions import (
    InvalidPOISubmissionState,
    POISubmissionNotFound,
)
from app.modules.poi_submission.domain.repositories.poi_submission_repository import (
    POISubmissionRepository,
)
from app.modules.poi_submission.infrastructure.persistence.poi_submission_document_mapper import (
    to_document,
    to_domain,
)


class MongoPOISubmissionRepository(POISubmissionRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, submission: POISubmission) -> POISubmission:
        document = to_document(submission)
        document["submiss_at"] = datetime.now(timezone.utc)
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return to_domain(document)

    def update_pending(self, submission: POISubmission) -> POISubmission:
        if submission.id is None or not ObjectId.is_valid(submission.id):
            raise POISubmissionNotFound("POI submission not found")
        result = self.collection.update_one(
            {
                "_id": ObjectId(submission.id),
                "review_status": ReviewStatus.PENDING.value,
                "submissed_by": ObjectId(submission.submissed_by),
            },
            {"$set": {"proposed_change": submission.proposed_change}},
        )
        self._raise_for_missing_or_reviewed(submission.id, result.matched_count)
        updated = self.collection.find_one({"_id": ObjectId(submission.id)})
        if updated is None:
            raise POISubmissionNotFound("POI submission not found after update")
        return to_domain(updated)

    def update_review(self, submission: POISubmission) -> POISubmission:
        if submission.id is None or not ObjectId.is_valid(submission.id):
            raise POISubmissionNotFound("POI submission not found")
        result = self.collection.update_one(
            {
                "_id": ObjectId(submission.id),
                "review_status": ReviewStatus.PENDING.value,
            },
            {
                "$set": {
                    "review_status": submission.review_status.value,
                    "admin_note": submission.admin_note,
                }
            },
        )
        self._raise_for_missing_or_reviewed(submission.id, result.matched_count)
        updated = self.collection.find_one({"_id": ObjectId(submission.id)})
        if updated is None:
            raise POISubmissionNotFound("POI submission not found after review")
        return to_domain(updated)

    def get_by_id(self, submission_id: str) -> POISubmission | None:
        if not ObjectId.is_valid(submission_id):
            return None
        document = self.collection.find_one({"_id": ObjectId(submission_id)})
        return to_domain(document) if document else None

    def get_by_submitter(self, submitter_id: str) -> list[POISubmission]:
        if not ObjectId.is_valid(submitter_id):
            return []
        documents = self.collection.find(
            {"submissed_by": ObjectId(submitter_id)}
        ).sort("submiss_at", -1)
        return [to_domain(document) for document in documents]

    def get_all(self) -> list[POISubmission]:
        documents = self.collection.find().sort("submiss_at", -1)
        return [to_domain(document) for document in documents]

    def delete_pending(self, submission_id: str, submitter_id: str) -> bool:
        if not ObjectId.is_valid(submission_id) or not ObjectId.is_valid(submitter_id):
            return False
        result = self.collection.delete_one(
            {
                "_id": ObjectId(submission_id),
                "submissed_by": ObjectId(submitter_id),
                "review_status": ReviewStatus.PENDING.value,
            }
        )
        return result.deleted_count > 0

    def delete(self, submission_id: str) -> bool:
        if not ObjectId.is_valid(submission_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(submission_id)})
        return result.deleted_count > 0

    def _raise_for_missing_or_reviewed(self, submission_id: str, matched: int) -> None:
        if matched:
            return
        existing = self.collection.find_one({"_id": ObjectId(submission_id)})
        if existing is None:
            raise POISubmissionNotFound("POI submission not found")
        raise InvalidPOISubmissionState("POI submission has already been reviewed")
