from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.infrastructure.database.mongo import get_database
from app.modules.menu.application.services.menu_item_service import MenuItemService
from app.modules.menu.infrastructure.repositories.mongo_menu_item_repository import (
    MongoMenuItemRepository,
)
from app.modules.poi.application.services.poi_service import POIService
from app.modules.poi.infrastructure.persistence.mongo_poi_repository import (
    MongoPOIRepository,
)
from app.modules.poi_submission.application.services.poi_submission_service import (
    POISubmissionService,
)
from app.modules.poi_submission.infrastructure.persistence.mongo_poi_submission_repository import (
    MongoPOISubmissionRepository,
)
from app.modules.registration.application.services.registration_service import (
    RegistrationService,
)
from app.modules.registration.infrastructure.persistence.mongo_registration_repository import (
    MongoRegistrationRepository,
)
from app.modules.role.application.services.role_service import RoleService
from app.modules.role.domain.entities.role import Role
from app.modules.role.infrastructure.persistence.mongo_role_repository import (
    MongoRoleRepository,
)
from app.modules.user.application.services.user_service import UserService
from app.modules.user.domain.entities.user import User, UserStatus
from app.modules.user.infrastructure.persistence.mongo_user_repository import (
    MongoUserRepository,
)
from app.modules.user.infrastructure.security.user_security import UserSecurity

bearer_scheme = HTTPBearer()


def get_menu_item_service() -> MenuItemService:
    database = get_database()
    collection = database["menu_items"]
    repository = MongoMenuItemRepository(collection)
    return MenuItemService(repository)


def get_poi_service() -> POIService:
    database = get_database()
    poi_repository = MongoPOIRepository(database["POI"])
    menu_item_repository = MongoMenuItemRepository(database["MenuItem"])
    return POIService(poi_repository, menu_item_repository)


def get_role_service() -> RoleService:
    database = get_database()
    repository = MongoRoleRepository(database["roles"])
    return RoleService(repository)


def get_user_service() -> UserService:
    database = get_database()
    user_collection = database["admin_users"]
    security = UserSecurity(
        encryption_key=settings.user_data_encryption_key,
        lookup_hmac_key=settings.user_lookup_hmac_key,
        jwt_secret_key=settings.jwt_secret_key,
        jwt_expiration_minutes=settings.jwt_expiration_minutes,
    )
    return UserService(
        user_repository=MongoUserRepository(user_collection),
        role_repository=MongoRoleRepository(database["roles"]),
        security=security,
    )


def get_registration_service() -> RegistrationService:
    database = get_database()
    repository = MongoRegistrationRepository(
        database["poi_owner_registrations"]
    )
    return RegistrationService(repository)


def get_poi_submission_service() -> POISubmissionService:
    database = get_database()
    return POISubmissionService(
        submission_repository=MongoPOISubmissionRepository(
            database["poi_submissions"]
        ),
        poi_service=get_poi_service(),
        menu_item_service=get_menu_item_service(),
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    try:
        user_id = service.security.decode_access_token(credentials.credentials)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    user = service.get_by_id(user_id)
    if user is None or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_user_permission(permission: str):
    def permission_checker(
        user: Annotated[User, Depends(get_current_user)],
        role_service: Annotated[RoleService, Depends(get_role_service)],
    ) -> Role:
        role = role_service.get_by_id(user.role_id)
        if role is None or permission not in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return role

    return permission_checker
