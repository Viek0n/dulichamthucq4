from dataclasses import dataclass
from datetime import datetime
from typing import Any
from app.domain.enumerators.review_status import ReviewStatus

@dataclass
class POI_Submission:
    _id: str
    slug: str
    proposed_change: dict[str, Any]
    submiss_at: datetime
    review_status: ReviewStatus
    admin_note: str
    for_poi: str
    submissed_by: str
