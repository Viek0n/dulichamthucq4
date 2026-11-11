from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from app.modules.registration.application.dto.registration_review_request import (
    RegistrationReviewRequest,
)
from app.modules.registration.application.services.registration_service import (
    RegistrationService,
)
from app.modules.registration.domain.entities.registration import Registration
from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)
from app.modules.registration.domain.exceptions.registration_exceptions import (
    InvalidRegistrationTransition,
    RegistrationNotFound,
)
from app.modules.registration.domain.states.registration_state import state_for
from app.modules.registration.infrastructure.persistence.mongo_registration_repository import (
    MongoRegistrationRepository,
)
from app.modules.registration.infrastructure.persistence.registration_document_mapper import (
    to_document,
    to_domain,
)


def _registration(
    status: RegistrationStatus = RegistrationStatus.PENDING,
) -> Registration:
    return Registration(
        id=str(ObjectId()),
        status=status,
        admin_note="",
        sender_id=str(ObjectId()),
        reviewer_id=None,
    )


def test_registration_state_allows_pending_review_once():
    registration = _registration()

    registration.accept(str(ObjectId()), "Approved")

    assert registration.status == RegistrationStatus.ACCEPTED
    assert registration.admin_note == "Approved"
    assert registration.reviewer_id is not None
    with pytest.raises(InvalidRegistrationTransition):
        registration.reject(str(ObjectId()), "Rejected")


def test_registration_state_allows_pending_rejection_and_blocks_acceptance():
    registration = _registration()
    reviewer_id = str(ObjectId())

    registration.reject(reviewer_id, "Incomplete information")

    assert registration.status == RegistrationStatus.REJECTED
    assert registration.reviewer_id == reviewer_id
    with pytest.raises(InvalidRegistrationTransition):
        registration.accept(reviewer_id, "Approved")


def test_registration_state_factory_returns_state_for_each_status():
    assert (
        state_for(RegistrationStatus.PENDING).status
        == RegistrationStatus.PENDING
    )
    assert (
        state_for(RegistrationStatus.ACCEPTED).status
        == RegistrationStatus.ACCEPTED
    )
    assert (
        state_for(RegistrationStatus.REJECTED).status
        == RegistrationStatus.REJECTED
    )


def test_registration_document_maps_object_ids_and_nullable_reviewer():
    registration = _registration()
    document = to_document(registration)

    assert document == {
        "status": "PENDING",
        "admin_note": "",
        "sender_id": ObjectId(registration.sender_id),
        "reviewer_id": None,
    }

    document["_id"] = ObjectId(registration.id)
    assert to_domain(document) == registration


def test_registration_repository_crud_and_pending_only_review_update():
    registration = _registration()
    document = to_document(registration)
    document["_id"] = ObjectId(registration.id)
    collection = MagicMock()
    collection.insert_one.return_value.inserted_id = document["_id"]
    collection.find_one.return_value = document
    collection.find.return_value = [document]
    collection.update_one.return_value.matched_count = 1
    collection.delete_one.return_value.deleted_count = 1
    repository = MongoRegistrationRepository(collection)

    assert repository.create(registration) == registration
    assert repository.get_by_id(registration.id) == registration
    assert repository.get_by_sender_id(registration.sender_id) == [registration]
    assert repository.get_all() == [registration]
    assert repository.update(registration) == registration
    collection.update_one.assert_called_once_with(
        {
            "_id": ObjectId(registration.id),
            "status": RegistrationStatus.PENDING.value,
        },
        {"$set": document_without_id(document)},
    )
    assert repository.delete(registration.id) is True
    assert repository.get_by_id("invalid-id") is None


def document_without_id(document: dict) -> dict:
    return {key: value for key, value in document.items() if key != "_id"}


def test_registration_repository_rejects_stale_review_updates():
    registration = _registration(RegistrationStatus.ACCEPTED)
    collection = MagicMock()
    collection.update_one.return_value.matched_count = 0
    collection.find_one.return_value = {"_id": ObjectId(registration.id)}
    repository = MongoRegistrationRepository(collection)

    with pytest.raises(InvalidRegistrationTransition):
        repository.update(registration)

    collection.find_one.return_value = None
    with pytest.raises(RegistrationNotFound):
        repository.update(registration)


def test_registration_repository_deletes_only_matching_pending_owner_request():
    registration = _registration()
    collection = MagicMock()
    collection.delete_one.return_value.deleted_count = 1
    repository = MongoRegistrationRepository(collection)

    assert repository.delete_pending(registration.id, registration.sender_id)
    collection.delete_one.assert_called_once_with(
        {
            "_id": ObjectId(registration.id),
            "sender_id": ObjectId(registration.sender_id),
            "status": RegistrationStatus.PENDING.value,
        }
    )


def test_registration_service_creates_pending_and_reviews():
    sender_id = str(ObjectId())
    reviewer_id = str(ObjectId())
    repository = MagicMock()
    repository.create.side_effect = lambda registration: registration
    registration = _registration()
    repository.get_by_id.return_value = registration
    repository.update.side_effect = lambda item: item
    service = RegistrationService(repository)

    created = service.create(sender_id)
    assert created.status == RegistrationStatus.PENDING
    assert created.sender_id == sender_id
    assert created.reviewer_id is None

    reviewed = service.review(
        registration.id,
        reviewer_id,
        RegistrationReviewRequest(status=RegistrationStatus.ACCEPTED, admin_note="OK"),
    )
    assert reviewed.status == RegistrationStatus.ACCEPTED
    assert reviewed.reviewer_id == reviewer_id
    with pytest.raises(ValueError):
        RegistrationReviewRequest(status=RegistrationStatus.PENDING)


def test_registration_service_deletes_only_owners_pending_registration():
    registration = _registration()
    repository = MagicMock()
    repository.get_by_id.return_value = registration
    repository.delete.return_value = True
    service = RegistrationService(repository)

    assert service.delete(registration.id, registration.sender_id) is True

    with pytest.raises(InvalidRegistrationTransition):
        service.delete(registration.id, str(ObjectId()))

    registration.status = RegistrationStatus.REJECTED
    with pytest.raises(InvalidRegistrationTransition):
        service.delete(registration.id, registration.sender_id)
    assert service.delete_as_moderator(registration.id) is True
