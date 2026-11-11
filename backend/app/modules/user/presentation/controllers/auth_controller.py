from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_user_service
from app.modules.user.application.dto.auth_requests import ChangePasswordRequest
from app.modules.user.application.dto.user_response import UserResponse
from app.modules.user.application.services.user_service import UserService
from app.modules.user.domain.entities.user import User

router = APIRouter(prefix="/admin/auth", tags=["Admin authentication"])


@router.get("/me", response_model=UserResponse)
def get_me(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return UserResponse.model_validate(service.to_response_data(user))


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    request: ChangePasswordRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        changed = service.change_password(
            user.id,
            request.current_password,
            request.new_password,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
