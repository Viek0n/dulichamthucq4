from bson import ObjectId

from app.modules.registration.domain.entities.registration import Registration
from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)


def to_domain(document: dict) -> Registration:
    reviewer_id = document["reviewer_id"]
    return Registration(
        id=str(document["_id"]),
        status=RegistrationStatus(document["status"]),
        admin_note=document["admin_note"],
        sender_id=str(document["sender_id"]),
        reviewer_id=str(reviewer_id) if reviewer_id is not None else None,
    )


def to_document(registration: Registration) -> dict:
    return {
        "status": registration.status.value,
        "admin_note": registration.admin_note,
        "sender_id": ObjectId(registration.sender_id),
        "reviewer_id": (
            ObjectId(registration.reviewer_id)
            if registration.reviewer_id is not None
            else None
        ),
    }
