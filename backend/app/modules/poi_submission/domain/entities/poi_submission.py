from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.modules.poi_submission.domain.enumerators.review_status import ReviewStatus


@dataclass
class POISubmission:
    id: str | None
    proposed_change: dict[str, Any]
    submiss_at: datetime
    review_status: ReviewStatus
    admin_note: str
    for_poi: str
    submissed_by: str

    def update_proposal(self, proposed_change: dict[str, Any]) -> None:
        if self.review_status != ReviewStatus.PENDING:
            raise ValueError("Only pending submissions can be changed")
        self.proposed_change = proposed_change

    def accept(self, admin_note: str) -> None:
        self._review(ReviewStatus.ACCEPTED, admin_note)

    def reject(self, admin_note: str) -> None:
        self._review(ReviewStatus.REJECTED, admin_note)

    def _review(self, status: ReviewStatus, admin_note: str) -> None:
        if self.review_status != ReviewStatus.PENDING:
            raise ValueError("Only pending submissions can be reviewed")
        self.review_status = status
        self.admin_note = admin_note
