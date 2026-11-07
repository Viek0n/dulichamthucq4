from enum import StrEnum

class MenuPermission(StrEnum):
    MENU_VIEW = "MENU_VIEW"
    MENU_CREATE = "MENU_CREATE"
    MENU_UPDATE = "MENU_UPDATE"
    MENU_DELETE = "MENU_DELETE"