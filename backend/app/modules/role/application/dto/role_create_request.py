from app.modules.role.domain.enumerators.permissions.permission_catalog import (
    ALL_PERMISSIONS,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    permissions: list[str]
    priority: int = Field(strict=True, ge=-(2**31), le=2**31 - 1)

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, permissions: list[str]) -> list[str]:
        invalid_permissions = sorted(set(permissions) - ALL_PERMISSIONS)
        if invalid_permissions:
            raise ValueError(f"Unknown permissions: {', '.join(invalid_permissions)}")
        if len(permissions) != len(set(permissions)):
            raise ValueError("Permissions must not contain duplicates")
        return permissions
