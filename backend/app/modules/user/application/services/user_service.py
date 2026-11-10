from typing import Literal

from app.modules.role.domain.repositories.role_repository import RoleRepository
from app.modules.user.application.dto.user_create_request import (
    UserCreateRequest,
    UserUpdateRequest,
)
from app.modules.user.domain.entities.user import User, UserStatus
from app.modules.user.domain.exceptions.user_exceptions import (
    UserAlreadyExists,
    UserNotFound,
)
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infrastructure.security.user_security import UserSecurity


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        security: UserSecurity,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.security = security

    def create(self, request: UserCreateRequest) -> User:
        email_hash = self.security.lookup_hash(str(request.email), "email")
        if self.user_repository.get_by_email_hash(email_hash):
            raise UserAlreadyExists("Email already exists")
        phone_hash = self.security.lookup_hash(request.phone, "phone")
        if self.user_repository.get_by_phone_hash(phone_hash):
            raise UserAlreadyExists("Phone already exists")
        self._ensure_role(request.role_id)

        return self.user_repository.create(
            User(
                id=None,
                password_hash=self.security.hash_password(request.password),
                is_poi_owner_verified=request.is_poi_owner_verified,
                status=request.status,
                name=request.name,
                email_encrypted=self.security.encrypt(str(request.email)),
                email_hash=email_hash,
                phone_encrypted=self.security.encrypt(request.phone),
                phone_hash=phone_hash,
                role_id=request.role_id,
            )
        )

    def get_by_id(self, user_id: str) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def get_all(self) -> list[User]:
        return self.user_repository.get_all()

    def update(self, user_id: str, request: UserUpdateRequest) -> User:
        existing = self.user_repository.get_by_id(user_id)
        if existing is None:
            raise UserNotFound("User not found")

        email_hash = self.security.lookup_hash(str(request.email), "email")
        email_owner = self.user_repository.get_by_email_hash(email_hash)
        if email_owner is not None and email_owner.id != user_id:
            raise UserAlreadyExists("Email already exists")

        phone_hash = self.security.lookup_hash(request.phone, "phone")
        phone_owner = self.user_repository.get_by_phone_hash(phone_hash)
        if phone_owner is not None and phone_owner.id != user_id:
            raise UserAlreadyExists("Phone already exists")

        self._ensure_role(request.role_id)

        return self.user_repository.update(
            User(
                id=existing.id,
                password_hash=(
                    self.security.hash_password(request.password)
                    if request.password is not None
                    else existing.password_hash
                ),
                is_poi_owner_verified=request.is_poi_owner_verified,
                status=request.status,
                name=request.name,
                email_encrypted=self.security.encrypt(str(request.email)),
                email_hash=email_hash,
                phone_encrypted=self.security.encrypt(request.phone),
                phone_hash=phone_hash,
                role_id=request.role_id,
            )
        )

    def delete(self, user_id: str) -> bool:
        return self.user_repository.soft_delete(user_id)

    def authenticate(
        self,
        identifier: str,
        password: str,
    ) -> User | None:
        identifier_type: Literal["email", "phone"] = (
            "email" if "@" in identifier else "phone"
        )
        lookup_hash = self.security.lookup_hash(identifier, identifier_type)
        user = (
            self.user_repository.get_by_email_hash(lookup_hash)
            if identifier_type == "email"
            else self.user_repository.get_by_phone_hash(lookup_hash)
        )

        if (
            user is None
            or user.status != UserStatus.ACTIVE
            or not self.security.verify_password(password, user.password_hash)
        ):
            return None
        return user

    def to_response_data(self, user: User) -> dict:
        return {
            "id": user.id,
            "is_poi_owner_verified": user.is_poi_owner_verified,
            "status": user.status,
            "name": user.name,
            "email": self.security.decrypt(user.email_encrypted),
            "phone": self.security.decrypt(user.phone_encrypted),
            "role_id": user.role_id,
        }

    def _ensure_role(self, role_id: str) -> None:
        if self.role_repository.get_by_id(role_id) is None:
            raise ValueError("Role not found")
