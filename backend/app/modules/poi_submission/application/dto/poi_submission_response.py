from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.modules.poi_submission.domain.enumerators.review_status import ReviewStatus


class POISubmissionResponse(BaseModel):
    id: str
    proposed_change: dict[str, Any]
    submiss_at: datetime
    review_status: ReviewStatus
    admin_note: str
    for_poi: str
    submissed_by: str
