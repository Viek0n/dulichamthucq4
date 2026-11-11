from dataclasses import dataclass

from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)
from app.modules.registration.domain.states.registration_state import state_for


@dataclass
class Registration:
    id: str | None
    status: RegistrationStatus
    admin_note: str
    sender_id: str
    reviewer_id: str | None

    def accept(self, reviewer_id: str, admin_note: str) -> None:
        state_for(self.status).accept(self, reviewer_id, admin_note)

    def reject(self, reviewer_id: str, admin_note: str) -> None:
        state_for(self.status).reject(self, reviewer_id, admin_note)
