from app.modules.registration.application.dto.registration_review_request import (
    RegistrationReviewRequest,
)
from app.modules.registration.domain.entities.registration import Registration
from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)
from app.modules.registration.domain.exceptions.registration_exceptions import (
    InvalidRegistrationTransition,
    RegistrationNotFound,
)
from app.modules.registration.domain.repositories.registration_repository import (
    RegistrationRepository,
)


class RegistrationService:
    def __init__(self, repository: RegistrationRepository):
        self.repository = repository

    def create(self, sender_id: str) -> Registration:
        return self.repository.create(
            Registration(
                id=None,
                status=RegistrationStatus.PENDING,
                admin_note="",
                sender_id=sender_id,
                reviewer_id=None,
            )
        )

    def get_by_id(self, registration_id: str) -> Registration | None:
        return self.repository.get_by_id(registration_id)

    def get_by_sender_id(self, sender_id: str) -> list[Registration]:
        return self.repository.get_by_sender_id(sender_id)

    def get_all(self) -> list[Registration]:
        return self.repository.get_all()

    def review(
        self,
        registration_id: str,
        reviewer_id: str,
        request: RegistrationReviewRequest,
    ) -> Registration:
        registration = self.repository.get_by_id(registration_id)
        if registration is None:
            raise RegistrationNotFound("Registration not found")

        if request.status == RegistrationStatus.ACCEPTED:
            registration.accept(reviewer_id, request.admin_note)
        elif request.status == RegistrationStatus.REJECTED:
            registration.reject(reviewer_id, request.admin_note)
        else:
            raise InvalidRegistrationTransition(
                "A registration review must accept or reject"
            )
        return self.repository.update(registration)

    def delete(self, registration_id: str, requester_id: str) -> bool:
        registration = self.repository.get_by_id(registration_id)
        if registration is None:
            return False
        if (
            registration.sender_id != requester_id
            or registration.status != RegistrationStatus.PENDING
        ):
            raise InvalidRegistrationTransition(
                "Only the sender can delete a pending registration"
            )
        if self.repository.delete_pending(registration_id, requester_id):
            return True

        latest = self.repository.get_by_id(registration_id)
        if latest is not None and (
            latest.sender_id != requester_id
            or latest.status != RegistrationStatus.PENDING
        ):
            raise InvalidRegistrationTransition(
                "Only the sender can delete a pending registration"
            )
        return False

    def delete_as_moderator(self, registration_id: str) -> bool:
        return self.repository.delete(registration_id)
