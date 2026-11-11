from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.dependencies import (
    get_current_user,
    get_registration_service,
    get_role_service,
    require_user_permission,
)
from app.modules.registration.application.dto.registration_response import (
    RegistrationResponse,
)
from app.modules.registration.application.dto.registration_review_request import (
    RegistrationReviewRequest,
)
from app.modules.registration.application.services.registration_service import (
    RegistrationService,
)
from app.modules.registration.domain.entities.registration import Registration
from app.modules.registration.domain.exceptions.registration_exceptions import (
    InvalidRegistrationTransition,
    RegistrationNotFound,
)
from app.modules.role.application.services.role_service import RoleService
from app.modules.role.domain.entities.role import Role
from app.modules.user.domain.entities.user import User

router = APIRouter(prefix="/registrations", tags=["Registrations"])
MODERATOR_PERMISSION = "content.moderate"


def to_response(registration: Registration) -> RegistrationResponse:
    return RegistrationResponse(
        id=registration.id,
        status=registration.status,
        admin_note=registration.admin_note,
        sender_id=registration.sender_id,
        reviewer_id=registration.reviewer_id,
    )


def is_moderator(user: User, roles: RoleService) -> bool:
    role = roles.get_by_id(user.role_id)
    return role is not None and MODERATOR_PERMISSION in role.permissions


@router.post(
    "",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_registration(
    user: Annotated[User, Depends(get_current_user)],
    _owner_role: Annotated[
        Role,
        Depends(require_user_permission("owner.register")),
    ],
    service: Annotated[RegistrationService, Depends(get_registration_service)],
):
    return to_response(service.create(user.id))


@router.get("", response_model=list[RegistrationResponse])
def get_registrations(
    _moderator: Annotated[
        Role,
        Depends(require_user_permission(MODERATOR_PERMISSION)),
    ],
    service: Annotated[RegistrationService, Depends(get_registration_service)],
):
    return [to_response(item) for item in service.get_all()]


@router.get("/mine", response_model=list[RegistrationResponse])
def get_my_registrations(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RegistrationService, Depends(get_registration_service)],
):
    return [
        to_response(item)
        for item in service.get_by_sender_id(user.id)
    ]


@router.get("/{registration_id}", response_model=RegistrationResponse)
def get_registration(
    registration_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RegistrationService, Depends(get_registration_service)],
    roles: Annotated[RoleService, Depends(get_role_service)],
):
    registration = service.get_by_id(registration_id)
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    if registration.sender_id != user.id and not is_moderator(user, roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access this registration",
        )
    return to_response(registration)


@router.put("/{registration_id}/review", response_model=RegistrationResponse)
def review_registration(
    registration_id: str,
    request: RegistrationReviewRequest,
    reviewer: Annotated[User, Depends(get_current_user)],
    _moderator: Annotated[
        Role,
        Depends(require_user_permission(MODERATOR_PERMISSION)),
    ],
    service: Annotated[RegistrationService, Depends(get_registration_service)],
):
    try:
        return to_response(
            service.review(registration_id, reviewer.id, request)
        )
    except RegistrationNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidRegistrationTransition as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete("/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_registration(
    registration_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RegistrationService, Depends(get_registration_service)],
    roles: Annotated[RoleService, Depends(get_role_service)],
):
    moderator = is_moderator(user, roles)
    try:
        deleted = (
            service.delete_as_moderator(registration_id)
            if moderator
            else service.delete(registration_id, user.id)
        )
    except InvalidRegistrationTransition as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
