from pydantic import BaseModel

from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)


class RegistrationResponse(BaseModel):
    id: str
    status: RegistrationStatus
    admin_note: str
    sender_id: str
    reviewer_id: str | None
