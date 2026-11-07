from enum import StrEnum

class POIPermission(StrEnum):
    POI_VIEW = "POI_VIEW"
    POI_CREATE = "POI_CREATE"
    POI_UPDATE = "POI_UPDATE"
    POI_DELETE = "POI_DELETE"