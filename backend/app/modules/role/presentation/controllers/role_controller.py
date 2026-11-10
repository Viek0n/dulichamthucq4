from typing import Annotated

from app.core.dependencies import get_role_service
from app.modules.role.application.dto.role_create_request import RoleCreateRequest
from app.modules.role.application.dto.role_response import RoleResponse
from app.modules.role.application.services.role_service import RoleService
from app.modules.role.domain.entities.role import Role
from app.modules.role.infrastructure.exceptions.role_exceptions import RoleNotFound
from fastapi import APIRouter, Depends, HTTPException, Response, status

router = APIRouter(prefix="/roles", tags=["Roles"])


def to_response(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        slug=role.slug,
        name=role.name,
        permissions=role.permissions,
        priority=role.priority,
    )


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    request: RoleCreateRequest,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    try:
        return to_response(service.create(request))
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get("", response_model=list[RoleResponse])
def get_roles(service: Annotated[RoleService, Depends(get_role_service)]):
    return [to_response(role) for role in service.get_all()]


@router.get("/slug/{slug}", response_model=RoleResponse)
def get_role_by_slug(
    slug: str,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    role = service.get_by_slug(slug)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return to_response(role)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: str,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    role = service.get_by_id(role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return to_response(role)


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: str,
    request: RoleCreateRequest,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    try:
        return to_response(service.update(role_id, request))
    except RoleNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: str,
    service: Annotated[RoleService, Depends(get_role_service)],
):
    if not service.delete(role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
