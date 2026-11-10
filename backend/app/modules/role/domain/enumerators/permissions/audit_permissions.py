from enum import StrEnum


class AuditPermission(StrEnum):
    READ = "audit.read"
    MANAGE = "audit.manage"
