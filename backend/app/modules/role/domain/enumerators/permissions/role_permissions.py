from enum import StrEnum


class RolePermission(StrEnum):
    READ = "role.read"
    CREATE = "role.create"
    UPDATE = "role.update"
    DELETE = "role.delete"

    ROLE_VIEW = READ
    ROLE_CREATE = CREATE
    ROLE_UPDATE = UPDATE
    ROLE_DELETE = DELETE
