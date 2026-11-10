from enum import StrEnum

class RolePermission(StrEnum):
    ROLE_VIEW = "ROLE_VIEW"
    ROLE_CREATE = "ROLE_CREATE"
    ROLE_UPDATE = "ROLE_UPDATE"
    ROLE_DELETE = "ROLE_DELETE"