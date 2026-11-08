from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any
from domain.enumerators.review_status import ReviewStatus

class POISubmissionCreateResponse(BaseModel):
    slug: str
    proposed_change: dict[str, Any]
    submiss_at: datetime
    review_status: ReviewStatus
    admin_note: str
    for_poi: str
    submissed_by: str