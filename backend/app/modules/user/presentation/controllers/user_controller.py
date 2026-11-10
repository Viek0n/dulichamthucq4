import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.dependencies import (
    get_role_service,
    get_user_service,
    require_user_permission,
)
from app.modules.role.application.services.role_service import RoleService
from app.modules.role.domain.entities.role import Role
from app.modules.user.application.dto.user_create_request import (
    UserCreateRequest,
    UserUpdateRequest,
)
from app.modules.user.application.dto.user_response import (
    UserResponse,
    UserTokenResponse,
)
from app.modules.user.application.services.user_service import UserService
from app.modules.user.domain.entities.user import User
from app.modules.user.domain.exceptions.user_exceptions import (
    UserAlreadyExists,
    UserNotFound,
)

router = APIRouter(prefix="/users", tags=["Admin users"])


class UserLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    identifier: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1)

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, identifier: str) -> str:
        if "@" in identifier:
            normalized = identifier.casefold()
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
                raise ValueError("Invalid email address")
            return normalized
        if len(identifier) > 32:
            raise ValueError("Phone number must not exceed 32 characters")
        return identifier


def to_response(user: User, service: UserService) -> UserResponse:
    return UserResponse.model_validate(service.to_response_data(user))


def ensure_role_assignable(target_role_id: str, actor_role: Role, roles: RoleService):
    target_role = roles.get_by_id(target_role_id)
    if target_role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role not found",
        )
    if not set(target_role.permissions).issubset(actor_role.permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign a role with permissions you do not have",
        )


@router.post("/login", response_model=UserTokenResponse)
def login(
    request: UserLoginRequest,
    service: Annotated[UserService, Depends(get_user_service)],
):
    user = service.authenticate(request.identifier, request.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserTokenResponse(access_token=service.security.create_access_token(user.id))


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    request: UserCreateRequest,
    actor_role: Annotated[Role, Depends(require_user_permission("user.create"))],
    service: Annotated[UserService, Depends(get_user_service)],
    roles: Annotated[RoleService, Depends(get_role_service)],
):
    ensure_role_assignable(request.role_id, actor_role, roles)
    try:
        return to_response(service.create(request), service)
    except UserAlreadyExists as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("", response_model=list[UserResponse])
def get_users(
    _actor_role: Annotated[Role, Depends(require_user_permission("user.read"))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return [to_response(user, service) for user in service.get_all()]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    _actor_role: Annotated[Role, Depends(require_user_permission("user.read"))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    user = service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return to_response(user, service)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UserUpdateRequest,
    actor_role: Annotated[Role, Depends(require_user_permission("user.update"))],
    service: Annotated[UserService, Depends(get_user_service)],
    roles: Annotated[RoleService, Depends(get_role_service)],
):
    ensure_role_assignable(request.role_id, actor_role, roles)
    try:
        return to_response(service.update(user_id, request), service)
    except UserNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except UserAlreadyExists as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    _actor_role: Annotated[Role, Depends(require_user_permission("user.delete"))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    if not service.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
