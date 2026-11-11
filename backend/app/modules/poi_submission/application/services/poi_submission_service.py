from datetime import datetime, timezone
from typing import cast

from pydantic import TypeAdapter

from app.modules.menu.application.dto.menu_item_create_request import (
    MenuItemCreateRequest,
)
from app.modules.menu.application.services.menu_item_service import MenuItemService
from app.modules.menu.domain.entities.menu_item import MenuItem
from app.modules.menu.infrastructure.exceptions.menu_item_exceptions import (
    MenuItemNotFound,
)
from app.modules.poi.application.dto.poi_create_request import POICreateRequest
from app.modules.poi.application.services.poi_service import POIService
from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.infrastructure.exceptions.poi_exceptions import POINotFound
from app.modules.poi_submission.application.dto.poi_submission_request import (
    POISubmissionCreateRequest,
    POISubmissionReviewRequest,
    POISubmissionUpdateRequest,
)
from app.modules.poi_submission.application.dto.proposed_change import (
    CreateMenuItemAction,
    DeleteMenuItemAction,
    ProposedChange,
    ProposedOperation,
    UpdateMenuItemAction,
    UpdatePOIAction,
)
from app.modules.poi_submission.domain.entities.poi_submission import POISubmission
from app.modules.poi_submission.domain.enumerators.review_status import ReviewStatus
from app.modules.poi_submission.domain.exceptions.poi_submission_exceptions import (
    InvalidPOISubmissionState,
    POISubmissionNotFound,
)
from app.modules.poi_submission.domain.repositories.poi_submission_repository import (
    POISubmissionRepository,
)

proposal_adapter = TypeAdapter(ProposedChange)


class POISubmissionService:
    def __init__(
        self,
        submission_repository: POISubmissionRepository,
        poi_service: POIService,
        menu_item_service: MenuItemService,
    ):
        self.submission_repository = submission_repository
        self.poi_service = poi_service
        self.menu_item_service = menu_item_service

    def create(
        self,
        request: POISubmissionCreateRequest,
        submitter_id: str,
    ) -> POISubmission:
        self._get_owned_poi(request.for_poi, submitter_id)
        proposal = request.proposed_change.model_dump(mode="json", exclude_unset=True)
        self._validate_operations(proposal, request.for_poi)
        return self.submission_repository.create(
            POISubmission(
                id=None,
                proposed_change=proposal,
                submiss_at=datetime.now(timezone.utc),
                review_status=ReviewStatus.PENDING,
                admin_note="",
                for_poi=request.for_poi,
                submissed_by=submitter_id,
            )
        )

    def get_by_id(self, submission_id: str) -> POISubmission | None:
        return self.submission_repository.get_by_id(submission_id)

    def get_by_submitter(self, submitter_id: str) -> list[POISubmission]:
        return self.submission_repository.get_by_submitter(submitter_id)

    def get_all(self) -> list[POISubmission]:
        return self.submission_repository.get_all()

    def update(
        self,
        submission_id: str,
        submitter_id: str,
        request: POISubmissionUpdateRequest,
    ) -> POISubmission:
        submission = self._get_pending_owned(submission_id, submitter_id)
        self._get_owned_poi(submission.for_poi, submitter_id)
        proposal = request.proposed_change.model_dump(
            mode="json",
            exclude_unset=True,
        )
        self._validate_operations(proposal, submission.for_poi)
        submission.update_proposal(proposal)
        return self.submission_repository.update_pending(submission)

    def review(
        self,
        submission_id: str,
        request: POISubmissionReviewRequest,
    ) -> POISubmission:
        submission = self.submission_repository.get_by_id(submission_id)
        if submission is None:
            raise POISubmissionNotFound("POI submission not found")
        if submission.review_status != ReviewStatus.PENDING:
            raise InvalidPOISubmissionState(
                "Only pending submissions can be reviewed"
            )

        if request.review_status == ReviewStatus.ACCEPTED.value:
            self._apply_proposal(submission)
            submission.accept(request.admin_note)
        else:
            submission.reject(request.admin_note)
        return self.submission_repository.update_review(submission)

    def delete(self, submission_id: str, submitter_id: str) -> bool:
        submission = self.submission_repository.get_by_id(submission_id)
        if submission is None:
            return False
        self._ensure_pending_owner(submission, submitter_id)
        if self.submission_repository.delete_pending(submission_id, submitter_id):
            return True
        self._raise_for_delete_race(submission_id, submitter_id)
        return False

    def delete_as_moderator(self, submission_id: str) -> bool:
        return self.submission_repository.delete(submission_id)

    def _apply_proposal(self, submission: POISubmission) -> None:
        poi = self.poi_service.get_by_id(submission.for_poi)
        if poi is None:
            raise POINotFound("POI not found")
        proposal = proposal_adapter.validate_python(submission.proposed_change)
        operations = cast(list[ProposedOperation], proposal.operations)
        self._validate_operations(submission.proposed_change, submission.for_poi)

        for operation in operations:
            if isinstance(operation, UpdatePOIAction):
                self._apply_poi_update(poi, operation)
                poi = self.poi_service.get_by_id(submission.for_poi)
                if poi is None:
                    raise POINotFound("POI not found after update")
            elif isinstance(operation, CreateMenuItemAction):
                self.menu_item_service.create(
                    MenuItemCreateRequest(
                        poi_id=submission.for_poi,
                        name=operation.name,
                        price=operation.price,
                    )
                )
            elif isinstance(operation, UpdateMenuItemAction):
                current = self._get_menu_item_for_poi(
                    operation.menu_item_id,
                    submission.for_poi,
                )
                self.menu_item_service.update(
                    operation.menu_item_id,
                    MenuItemCreateRequest(
                        poi_id=current.poi_id,
                        name=(
                            operation.name
                            if operation.name is not None
                            else current.name
                        ),
                        price=(
                            operation.price
                            if operation.price is not None
                            else current.price
                        ),
                    ),
                )
            elif isinstance(operation, DeleteMenuItemAction):
                self._get_menu_item_for_poi(
                    operation.menu_item_id,
                    submission.for_poi,
                )
                if not self.menu_item_service.delete(operation.menu_item_id):
                    raise MenuItemNotFound("Menu item not found")

    def _apply_poi_update(self, poi: POI, action: UpdatePOIAction) -> None:
        self.poi_service.update(
            cast(str, poi.id),
            _poi_update_request(poi, action),
        )

    def _validate_operations(
        self,
        proposed_change: dict,
        poi_id: str | None,
    ) -> None:
        if poi_id is None:
            raise POINotFound("POI not found")
        proposal = proposal_adapter.validate_python(proposed_change)
        for operation in proposal.operations:
            if isinstance(operation, UpdatePOIAction):
                poi = self.poi_service.get_by_id(poi_id)
                if poi is None:
                    raise POINotFound("POI not found")
                _poi_update_request(poi, operation)
            elif isinstance(
                operation,
                (UpdateMenuItemAction, DeleteMenuItemAction),
            ):
                self._get_menu_item_for_poi(operation.menu_item_id, poi_id)

    def _get_menu_item_for_poi(self, menu_item_id: str, poi_id: str) -> MenuItem:
        menu_item = self.menu_item_service.get_by_id(menu_item_id)
        if menu_item is None or menu_item.poi_id != poi_id:
            raise MenuItemNotFound("Menu item not found for this POI")
        return menu_item

    def _get_owned_poi(self, poi_id: str, submitter_id: str) -> POI:
        poi = self.poi_service.get_by_id(poi_id)
        if poi is None:
            raise POINotFound("POI not found")
        if poi.poi_owner_id != submitter_id:
            raise InvalidPOISubmissionState(
                "Only the POI owner can submit changes"
            )
        return poi

    def _get_pending_owned(
        self,
        submission_id: str,
        submitter_id: str,
    ) -> POISubmission:
        submission = self.submission_repository.get_by_id(submission_id)
        if submission is None:
            raise POISubmissionNotFound("POI submission not found")
        self._ensure_pending_owner(submission, submitter_id)
        return submission

    @staticmethod
    def _ensure_pending_owner(
        submission: POISubmission,
        submitter_id: str,
    ) -> None:
        if submission.submissed_by != submitter_id:
            raise InvalidPOISubmissionState(
                "Only the submitter can modify this submission"
            )
        if submission.review_status != ReviewStatus.PENDING:
            raise InvalidPOISubmissionState(
                "Only pending submissions can be modified"
            )

    def _raise_for_delete_race(self, submission_id: str, submitter_id: str) -> None:
        latest = self.submission_repository.get_by_id(submission_id)
        if latest is not None:
            self._ensure_pending_owner(latest, submitter_id)


def _poi_update_request(poi: POI, action: UpdatePOIAction) -> POICreateRequest:
    values = {
        "name": poi.name,
        "address": poi.address,
        "open_at": str(poi.open_at.time),
        "close_at": str(poi.close_at.time),
        "contact": poi.contact,
        "description": poi.description,
        "image": poi.image,
        "latitude": poi.position.latitude,
        "longitude": poi.position.longitude,
        "trigger_radius": poi.trigger_radius,
    }
    values.update(action.changes.model_dump(exclude_unset=True))
    return POICreateRequest.model_validate(values)
