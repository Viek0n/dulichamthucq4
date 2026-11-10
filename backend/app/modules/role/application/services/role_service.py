from app.modules.role.application.dto.role_create_request import RoleCreateRequest
from app.modules.role.domain.entities.role import Role
from app.modules.role.domain.repositories.role_repository import RoleRepository
from app.modules.role.infrastructure.exceptions.role_exceptions import RoleNotFound


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def create(self, request: RoleCreateRequest) -> Role:
        return self.role_repository.create(self._to_role(request, role_id=None))

    def get_by_id(self, role_id: str) -> Role | None:
        return self.role_repository.get_by_id(role_id)

    def get_all(self) -> list[Role]:
        return self.role_repository.get_all()

    def update(self, role_id: str, request: RoleCreateRequest) -> Role:
        existing_role = self.role_repository.get_by_id(role_id)
        if existing_role is None:
            raise RoleNotFound("Role not found")

        return self.role_repository.update(
            self._to_role(request, role_id=existing_role.id)
        )

    def delete(self, role_id: str) -> bool:
        return self.role_repository.delete(role_id)

    @staticmethod
    def _to_role(request: RoleCreateRequest, role_id: str | None) -> Role:
        return Role(
            id=role_id,
            name=request.name,
            permissions=request.permissions,
            priority=request.priority,
        )
