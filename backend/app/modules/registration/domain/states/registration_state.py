from abc import ABC
from typing import TYPE_CHECKING

from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)
from app.modules.registration.domain.exceptions.registration_exceptions import (
    InvalidRegistrationTransition,
)

if TYPE_CHECKING:
    from app.modules.registration.domain.entities.registration import Registration


class RegistrationState(ABC):
    status: RegistrationStatus

    def accept(
        self,
        registration: "Registration",
        reviewer_id: str,
        admin_note: str,
    ) -> None:
        raise InvalidRegistrationTransition(
            f"Cannot accept a {self.status.value.lower()} registration"
        )

    def reject(
        self,
        registration: "Registration",
        reviewer_id: str,
        admin_note: str,
    ) -> None:
        raise InvalidRegistrationTransition(
            f"Cannot reject a {self.status.value.lower()} registration"
        )


class PendingRegistrationState(RegistrationState):
    status = RegistrationStatus.PENDING

    def accept(
        self,
        registration: "Registration",
        reviewer_id: str,
        admin_note: str,
    ) -> None:
        registration.status = RegistrationStatus.ACCEPTED
        registration.reviewer_id = reviewer_id
        registration.admin_note = admin_note

    def reject(
        self,
        registration: "Registration",
        reviewer_id: str,
        admin_note: str,
    ) -> None:
        registration.status = RegistrationStatus.REJECTED
        registration.reviewer_id = reviewer_id
        registration.admin_note = admin_note


class AcceptedRegistrationState(RegistrationState):
    status = RegistrationStatus.ACCEPTED


class RejectedRegistrationState(RegistrationState):
    status = RegistrationStatus.REJECTED


def state_for(status: RegistrationStatus) -> RegistrationState:
    states: dict[RegistrationStatus, type[RegistrationState]] = {
        RegistrationStatus.PENDING: PendingRegistrationState,
        RegistrationStatus.ACCEPTED: AcceptedRegistrationState,
        RegistrationStatus.REJECTED: RejectedRegistrationState,
    }
    return states[status]()
