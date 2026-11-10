from enum import StrEnum


class MenuPermission(StrEnum):
    READ = "menu.read"
    CREATE = "menu.create"
    UPDATE = "menu.update"
    DELETE = "menu.delete"

    MENU_VIEW = READ
    MENU_CREATE = CREATE
    MENU_UPDATE = UPDATE
    MENU_DELETE = DELETE
