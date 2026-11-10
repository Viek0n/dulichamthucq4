from abc import ABC, abstractmethod

from app.modules.menu.domain.entities.menu_item import MenuItem


class MenuItemRepository(ABC):
    @abstractmethod
    def create(self, menu_item: MenuItem) -> MenuItem:
        pass

    @abstractmethod
    def update(self, menu_item: MenuItem) -> MenuItem:
        pass

    @abstractmethod
    def delete(self, menu_item_id: str) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, menu_item_id: str) -> MenuItem | None:
        pass

    @abstractmethod
    def get_by_poi_id(self, poi_id: str) -> list[MenuItem]:
        pass

    @abstractmethod
    def delete_by_poi_id(self, poi_id: str) -> int:
        pass
