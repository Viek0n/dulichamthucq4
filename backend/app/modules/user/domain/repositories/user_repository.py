from abc import ABC, abstractmethod

from app.modules.user.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def soft_delete(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> User | None:
        pass

    @abstractmethod
    def get_by_email_hash(self, email_hash: str) -> User | None:
        pass

    @abstractmethod
    def get_by_phone_hash(self, phone_hash: str) -> User | None:
        pass

    @abstractmethod
    def get_all(self) -> list[User]:
        pass
