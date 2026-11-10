from enum import StrEnum


class AnalyticsPermission(StrEnum):
    VIEW = "analytics.view"
    EXPORT = "analytics.export"
    VIEW_OWN = "analytics.view_own"
