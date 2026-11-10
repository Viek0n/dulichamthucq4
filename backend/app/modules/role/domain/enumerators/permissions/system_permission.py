from enum import StrEnum


class SystemPermission(StrEnum):
    CONFIG = "system.config"
    LOGS = "system.logs"
    BACKUP = "system.backup"
