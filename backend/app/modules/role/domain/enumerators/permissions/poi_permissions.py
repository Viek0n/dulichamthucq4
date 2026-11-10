from enum import StrEnum


class POIPermission(StrEnum):
    READ = "poi.read"
    CREATE = "poi.create"
    UPDATE = "poi.update"
    DELETE = "poi.delete"
    APPROVE = "poi.approve"
    TOGGLE = "poi.toggle"

    POI_VIEW = READ
    POI_CREATE = CREATE
    POI_UPDATE = UPDATE
    POI_DELETE = DELETE
