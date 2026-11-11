from abc import ABC, abstractmethod

from app.modules.registration.domain.entities.registration import Registration


class RegistrationRepository(ABC):
    @abstractmethod
    def create(self, registration: Registration) -> Registration:
        pass

    @abstractmethod
    def get_by_id(self, registration_id: str) -> Registration | None:
        pass

    @abstractmethod
    def get_by_sender_id(self, sender_id: str) -> list[Registration]:
        pass

    @abstractmethod
    def get_all(self) -> list[Registration]:
        pass

    @abstractmethod
    def update(self, registration: Registration) -> Registration:
        pass

    @abstractmethod
    def delete(self, registration_id: str) -> bool:
        pass

    @abstractmethod
    def delete_pending(self, registration_id: str, sender_id: str) -> bool:
        pass
