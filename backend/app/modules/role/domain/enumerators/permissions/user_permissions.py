from enum import StrEnum


class UserPermission(StrEnum):
    READ = "user.read"
    CREATE = "user.create"
    UPDATE = "user.update"
    DELETE = "user.delete"

    USER_VIEW = READ
    USER_CREATE = CREATE
    USER_UPDATE = UPDATE
    USER_DELETE = DELETE
