from abc import ABC, abstractmethod

from app.modules.role.domain.entities.role import Role


class RoleRepository(ABC):
    @abstractmethod
    def create(self, role: Role) -> Role:
        pass

    @abstractmethod
    def update(self, role: Role) -> Role:
        pass

    @abstractmethod
    def delete(self, role_id: str) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, role_id: str) -> Role | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Role]:
        pass
