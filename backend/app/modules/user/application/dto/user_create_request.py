import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.user.domain.entities.user import UserStatus


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    password: str = Field(min_length=8, max_length=72)
    is_poi_owner_verified: bool = False
    status: UserStatus = UserStatus.ACTIVE
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=254)
    phone: str = Field(min_length=3, max_length=32)
    role_id: str = Field(pattern=r"^[a-fA-F0-9]{24}$")

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return password

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        normalized = email.strip().casefold()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Invalid email address")
        return normalized

    @field_validator("status")
    @classmethod
    def prevent_creating_soft_deleted_user(cls, status: UserStatus) -> UserStatus:
        if status == UserStatus.SOFT_DELETE:
            raise ValueError("Use the delete endpoint to soft-delete a user")
        return status


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    password: str | None = Field(default=None, min_length=8, max_length=72)
    is_poi_owner_verified: bool
    status: UserStatus
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=254)
    phone: str = Field(min_length=3, max_length=32)
    role_id: str = Field(pattern=r"^[a-fA-F0-9]{24}$")

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, password: str | None) -> str | None:
        if password is not None and len(password.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return password

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        normalized = email.strip().casefold()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Invalid email address")
        return normalized

    @field_validator("status")
    @classmethod
    def prevent_updating_to_soft_deleted_user(cls, status: UserStatus) -> UserStatus:
        if status == UserStatus.SOFT_DELETE:
            raise ValueError("Use the delete endpoint to soft-delete a user")
        return status
