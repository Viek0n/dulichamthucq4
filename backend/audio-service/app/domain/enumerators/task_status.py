from enum import Enum

class TaskStatus(Enum):
    PROGRESSING = "PROGRESSING", 
    FINISH = "FINISH", 
    PAUSE = "PAUSE", 
    CANCELLED = "CANCELLED",
    FAILED = "FAILED"