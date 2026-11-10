from dataclasses import dataclass
from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SOFT_DELETE = "SOFT_DELETE"


@dataclass
class User:
    id: str | None
    slug: str
    password_hash: str
    is_poi_owner_verified: bool
    status: UserStatus
    name: str
    email_encrypted: str
    email_hash: str
    phone_encrypted: str
    phone_hash: str
    role_id: str
