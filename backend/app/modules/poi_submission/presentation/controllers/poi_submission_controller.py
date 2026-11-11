from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.dependencies import (
    get_current_user,
    get_poi_submission_service,
    get_role_service,
    require_user_permission,
)
from app.modules.menu.infrastructure.exceptions.menu_item_exceptions import (
    MenuItemNotFound,
)
from app.modules.poi.infrastructure.exceptions.poi_exceptions import POINotFound
from app.modules.poi_submission.application.dto.poi_submission_request import (
    POISubmissionCreateRequest,
    POISubmissionReviewRequest,
    POISubmissionUpdateRequest,
)
from app.modules.poi_submission.application.dto.poi_submission_response import (
    POISubmissionResponse,
)
from app.modules.poi_submission.application.services.poi_submission_service import (
    POISubmissionService,
)
from app.modules.poi_submission.domain.entities.poi_submission import POISubmission
from app.modules.poi_submission.domain.exceptions.poi_submission_exceptions import (
    InvalidPOISubmissionState,
    POISubmissionNotFound,
)
from app.modules.role.application.services.role_service import RoleService
from app.modules.role.domain.entities.role import Role
from app.modules.user.domain.entities.user import User

router = APIRouter(prefix="/poi-submissions", tags=["POI submissions"])
MODERATOR_PERMISSION = "content.moderate"


def to_response(submission: POISubmission) -> POISubmissionResponse:
    return POISubmissionResponse(
        id=submission.id,
        proposed_change=submission.proposed_change,
        submiss_at=submission.submiss_at,
        review_status=submission.review_status,
        admin_note=submission.admin_note,
        for_poi=submission.for_poi,
        submissed_by=submission.submissed_by,
    )


def is_moderator(user: User, roles: RoleService) -> bool:
    role = roles.get_by_id(user.role_id)
    return role is not None and MODERATOR_PERMISSION in role.permissions


@router.post(
    "",
    response_model=POISubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_poi_submission(
    request: POISubmissionCreateRequest,
    user: Annotated[User, Depends(get_current_user)],
    _submit_permission: Annotated[
        Role,
        Depends(require_user_permission("owner.submit_poi")),
    ],
    service: Annotated[POISubmissionService, Depends(get_poi_submission_service)],
):
    try:
        return to_response(service.create(request, user.id))
    except POINotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidPOISubmissionState as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    except MenuItemNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/mine", response_model=list[POISubmissionResponse])
def get_my_poi_submissions(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[POISubmissionService, Depends(get_poi_submission_service)],
):
    return [
        to_response(item)
        for item in service.get_by_submitter(user.id)
    ]


@router.get("", response_model=list[POISubmissionResponse])
def get_poi_submissions(
    _moderator: Annotated[
        Role,
        Depends(require_user_permission(MODERATOR_PERMISSION)),
    ],
    service: Annotated[POISubmissionService, Depends(get_poi_submission_service)],
):
    return [to_response(item) for item in service.get_all()]


@router.get("/{submission_id}", response_model=POISubmissionResponse)
def get_poi_submission(
    submission_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[POISubmissionService, Depends(get_poi_submission_service)],
    roles: Annotated[RoleService, Depends(get_role_service)],
):
    submission = service.get_by_id(submission_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POI submission not found",
        )
    if submission.submissed_by != user.id and not is_moderator(user, roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access this POI submission",
        )
    return to_response(submission)


@router.put("/{submission_id}", response_model=POISubmissionResponse)
def update_poi_submission(
    submission_id: str,
    request: POISubmissionUpdateRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[POISubmissionService, Depends(get_poi_submission_service)],
):
    try:
        return to_response(service.update(submission_id, user.id, request))
    except POISubmissionNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidPOISubmissionState as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except POINotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except MenuItemNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.put("/{submission_id}/review", response_model=POISubmissionResponse)
def review_poi_submission(
    submission_id: str,
    request: POISubmissionReviewRequest,
    _moderator: Annotated[
        Role,
        Depends(require_user_permission(MODERATOR_PERMISSION)),
    ],
    service: Annotated[POISubmissionService, Depends(get_poi_submission_service)],
):
    try:
        return to_response(service.review(submission_id, request))
    except POISubmissionNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidPOISubmissionState as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except (POINotFound, MenuItemNotFound) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poi_submission(
    submission_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[POISubmissionService, Depends(get_poi_submission_service)],
    roles: Annotated[RoleService, Depends(get_role_service)],
):
    try:
        deleted = (
            service.delete_as_moderator(submission_id)
            if is_moderator(user, roles)
            else service.delete(submission_id, user.id)
        )
    except InvalidPOISubmissionState as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POI submission not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
