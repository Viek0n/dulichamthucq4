from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.poi_submission.application.dto.proposed_change import ProposedChange
from app.modules.poi_submission.domain.enumerators.review_status import ReviewStatus


class POISubmissionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    for_poi: str = Field(pattern=r"^[a-fA-F0-9]{24}$")
    proposed_change: ProposedChange


class POISubmissionUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposed_change: ProposedChange


class POISubmissionReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    review_status: Literal[ReviewStatus.ACCEPTED, ReviewStatus.REJECTED]
    admin_note: str = Field(default="", max_length=2000)
