from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from app.modules.menu.domain.entities.menu_item import MenuItem
from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.domain.value_objects.at_time import AtTime
from app.modules.poi.domain.value_objects.coordinate import Coordinate
from app.modules.poi_submission.application.dto.poi_submission_request import (
    POISubmissionCreateRequest,
    POISubmissionReviewRequest,
    POISubmissionUpdateRequest,
)
from app.modules.poi_submission.application.services.poi_submission_service import (
    POISubmissionService,
)
from app.modules.poi_submission.domain.entities.poi_submission import POISubmission
from app.modules.poi_submission.domain.enumerators.review_status import ReviewStatus
from app.modules.poi_submission.domain.exceptions.poi_submission_exceptions import (
    InvalidPOISubmissionState,
)
from app.modules.poi_submission.infrastructure.persistence.mongo_poi_submission_repository import (
    MongoPOISubmissionRepository,
)


def _poi(poi_id: str | None = None, owner_id: str | None = None) -> POI:
    return POI(
        id=poi_id or str(ObjectId()),
        name="Old name",
        address="Old address",
        open_at=AtTime("08:00"),
        close_at=AtTime("17:00"),
        contact="123",
        description="",
        image="",
        position=Coordinate(latitude=10, longitude=106),
        poi_owner_id=owner_id or str(ObjectId()),
    )


def _submission(
    poi_id: str,
    submitter_id: str,
    proposed_change: dict | None = None,
) -> POISubmission:
    return POISubmission(
        id=str(ObjectId()),
        proposed_change=proposed_change
        or {
            "operations": [
                {
                    "action": "update_poi",
                    "changes": {"name": "New name"},
                }
            ]
        },
        submiss_at=datetime.now(timezone.utc),
        review_status=ReviewStatus.PENDING,
        admin_note="",
        for_poi=poi_id,
        submissed_by=submitter_id,
    )


def test_submission_repository_maps_and_cruds_records():
    poi_id = ObjectId()
    submitter_id = ObjectId()
    submission_id = ObjectId()
    document = {
        "_id": submission_id,
        "proposed_change": {"operations": [{"action": "delete_menu_item"}]},
        "submiss_at": datetime.now(timezone.utc),
        "review_status": "PENDING",
        "admin_note": "",
        "for_poi": poi_id,
        "submissed_by": submitter_id,
    }
    collection = MagicMock()
    collection.insert_one.return_value.inserted_id = submission_id
    collection.find_one.return_value = document
    collection.find.return_value.sort.return_value = [document]
    collection.delete_one.return_value.deleted_count = 1
    collection.update_one.return_value.matched_count = 1
    repository = MongoPOISubmissionRepository(collection)
    submission = repository.create(
        POISubmission(
            id=None,
            proposed_change=document["proposed_change"],
            submiss_at=document["submiss_at"],
            review_status=ReviewStatus.PENDING,
            admin_note="",
            for_poi=str(poi_id),
            submissed_by=str(submitter_id),
        )
    )

    assert submission.id == str(submission_id)
    loaded = repository.get_by_id(str(submission_id))
    assert loaded is not None
    assert loaded.proposed_change == submission.proposed_change
    assert loaded.for_poi == submission.for_poi
    assert repository.get_by_submitter(str(submitter_id)) == [loaded]
    assert repository.get_all() == [loaded]
    submission.proposed_change = {"operations": []}
    repository.update_pending(submission)
    collection.update_one.assert_called_with(
        {
            "_id": submission_id,
            "review_status": ReviewStatus.PENDING.value,
            "submissed_by": submitter_id,
        },
        {"$set": {"proposed_change": {"operations": []}}},
    )
    submission.reject("No")
    repository.update_review(submission)
    assert repository.delete_pending(str(submission_id), str(submitter_id))
    assert repository.delete(str(submission_id))
    assert repository.get_by_id("invalid-id") is None


def test_submission_service_creates_owned_pending_submission():
    poi = _poi()
    repository = MagicMock()
    repository.create.side_effect = lambda item: item
    poi_service = MagicMock()
    poi_service.get_by_id.return_value = poi
    service = POISubmissionService(repository, poi_service, MagicMock())
    request = POISubmissionCreateRequest(
        for_poi=poi.id,
        proposed_change={
            "operations": [
                {"action": "update_poi", "changes": {"name": "Proposed"}}
            ]
        },
    )

    created = service.create(request, poi.poi_owner_id)

    assert created.review_status == ReviewStatus.PENDING
    assert created.submissed_by == poi.poi_owner_id
    assert created.proposed_change == request.proposed_change.model_dump(
        mode="json",
        exclude_unset=True,
    )

    with pytest.raises(InvalidPOISubmissionState):
        service.create(request, str(ObjectId()))


def test_submission_service_update_is_limited_to_submitter_pending_record():
    poi = _poi()
    submission = _submission(poi.id, poi.poi_owner_id)
    repository = MagicMock()
    repository.get_by_id.return_value = submission
    repository.update_pending.side_effect = lambda item: item
    poi_service = MagicMock()
    poi_service.get_by_id.return_value = poi
    service = POISubmissionService(repository, poi_service, MagicMock())
    request = POISubmissionUpdateRequest(
        proposed_change={
            "operations": [
                {"action": "update_poi", "changes": {"contact": "555"}}
            ]
        }
    )

    assert service.update(submission.id, poi.poi_owner_id, request) == submission
    with pytest.raises(InvalidPOISubmissionState):
        service.update(submission.id, str(ObjectId()), request)

    submission.accept("Approved")
    with pytest.raises(InvalidPOISubmissionState):
        service.update(submission.id, poi.poi_owner_id, request)


def test_submission_acceptance_applies_poi_and_menu_actions():
    poi = _poi()
    submitter_id = poi.poi_owner_id
    menu_item_id = str(ObjectId())
    submission = _submission(
        poi.id,
        submitter_id,
        {
            "operations": [
                {
                    "action": "update_poi",
                    "changes": {
                        "name": "Updated name",
                        "latitude": 12,
                    },
                },
                {
                    "action": "create_menu_item",
                    "name": "New dish",
                    "price": 99,
                },
                {
                    "action": "update_menu_item",
                    "menu_item_id": menu_item_id,
                    "price": 120,
                },
                {
                    "action": "delete_menu_item",
                    "menu_item_id": menu_item_id,
                },
            ]
        },
    )
    repository = MagicMock()
    repository.get_by_id.return_value = submission
    repository.update_review.side_effect = lambda item: item
    poi_service = MagicMock()
    poi_service.get_by_id.return_value = poi
    menu_service = MagicMock()
    menu_service.get_by_id.return_value = MenuItem(
        id=menu_item_id,
        poi_id=poi.id,
        name="Old dish",
        price=100,
    )
    menu_service.delete.return_value = True
    service = POISubmissionService(repository, poi_service, menu_service)

    reviewed = service.review(
        submission.id,
        POISubmissionReviewRequest(
            review_status=ReviewStatus.ACCEPTED,
            admin_note="Approved",
        ),
    )

    assert reviewed.review_status == ReviewStatus.ACCEPTED
    assert reviewed.admin_note == "Approved"
    poi_service.update.assert_called_once()
    poi_request = poi_service.update.call_args.args[1]
    assert poi_request.name == "Updated name"
    assert poi_request.latitude == 12
    menu_service.create.assert_called_once()
    assert menu_service.create.call_args.args[0].name == "New dish"
    menu_service.update.assert_called_once()
    assert menu_service.update.call_args.args[1].price == 120
    menu_service.delete.assert_called_once_with(menu_item_id)


def test_rejection_does_not_apply_proposed_changes():
    poi = _poi()
    submission = _submission(poi.id, poi.poi_owner_id)
    repository = MagicMock()
    repository.get_by_id.return_value = submission
    repository.update_review.side_effect = lambda item: item
    poi_service = MagicMock()
    service = POISubmissionService(repository, poi_service, MagicMock())

    reviewed = service.review(
        submission.id,
        POISubmissionReviewRequest(
            review_status=ReviewStatus.REJECTED,
            admin_note="Please revise",
        ),
    )

    assert reviewed.review_status == ReviewStatus.REJECTED
    poi_service.update.assert_not_called()


def test_proposal_validation_rejects_empty_and_unknown_operations():
    with pytest.raises(ValueError):
        POISubmissionCreateRequest(
            for_poi=str(ObjectId()),
            proposed_change={"operations": []},
        )
    with pytest.raises(ValueError):
        POISubmissionCreateRequest(
            for_poi=str(ObjectId()),
            proposed_change={
                "operations": [{"action": "execute_arbitrary_command"}]
            },
        )
