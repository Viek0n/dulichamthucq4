from bson import ObjectId

from app.modules.poi_submission.domain.entities.poi_submission import POISubmission
from app.modules.poi_submission.domain.enumerators.review_status import ReviewStatus


def to_domain(document: dict) -> POISubmission:
    return POISubmission(
        id=str(document["_id"]),
        proposed_change=document["proposed_change"],
        submiss_at=document["submiss_at"],
        review_status=ReviewStatus(document["review_status"]),
        admin_note=document["admin_note"],
        for_poi=str(document["for_poi"]),
        submissed_by=str(document["submissed_by"]),
    )


def to_document(submission: POISubmission) -> dict:
    return {
        "proposed_change": submission.proposed_change,
        "submiss_at": submission.submiss_at,
        "review_status": submission.review_status.value,
        "admin_note": submission.admin_note,
        "for_poi": ObjectId(submission.for_poi),
        "submissed_by": ObjectId(submission.submissed_by),
    }
