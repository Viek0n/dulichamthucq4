from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)


class RegistrationReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: Literal[
        RegistrationStatus.ACCEPTED,
        RegistrationStatus.REJECTED,
    ]
    admin_note: str = Field(default="", max_length=2000)
