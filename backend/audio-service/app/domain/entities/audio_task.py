from dataclasses import dataclass
from datetime import datetime
from app.domain.enumerators.task_status import TaskStatus

@dataclass
class AudioTask():
    _id: str
    localization_id: str
    status: TaskStatus
    attempts: int
    heartbeat_at: datetime
    created_at: datetime
    expire_at: datetime