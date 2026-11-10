from enum import StrEnum


class OwnerPermission(StrEnum):
    REGISTER = "owner.register"
    ACCESS = "owner.access"
    SUBMIT_POI = "owner.submit_poi"
    MANAGE_OWN_POI = "owner.manage_own_poi"
