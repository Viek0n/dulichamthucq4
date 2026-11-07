from abc import ABC, abstractmethod
from app.domain.entities.menu_item import MenuItem

class MenuItemRepository(ABC):
    @abstractmethod
    def create(self, poi_submission: MenuItem) -> MenuItem:
        pass

    @abstractmethod
    def update(self, poi_submission:MenuItem) -> MenuItem:
        pass

    @abstractmethod
    def delete(self, poi_submission:MenuItem) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, poi_submission:MenuItem) -> MenuItem | None:
        pass

    @abstractmethod
    def get_by_slug(self, poi_submission:MenuItem) -> MenuItem | None:
        pass