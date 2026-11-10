from app.modules.menu.application.dto.menu_item_create_request import (
    MenuItemCreateRequest,
)
from app.modules.menu.domain.entities.menu_item import MenuItem
from app.modules.menu.domain.repositories.menu_item_repository import MenuItemRepository


class MenuItemService:
    def __init__(self, menu_item_repository: MenuItemRepository):
        self.menu_item_repository = menu_item_repository

    def create(self, request: MenuItemCreateRequest) -> MenuItem:
        return self.menu_item_repository.create(
            MenuItem(
                id=None,
                poi_id=request.poi_id,
                name=request.name,
                price=request.price,
            )
        )

    def get_by_id(self, menu_item_id: str) -> MenuItem | None:
        return self.menu_item_repository.get_by_id(menu_item_id)

    def get_by_poi_id(self, poi_id: str) -> list[MenuItem]:
        return self.menu_item_repository.get_by_poi_id(poi_id)

    def update(self, menu_item_id: str, request: MenuItemCreateRequest) -> MenuItem:
        return self.menu_item_repository.update(
            MenuItem(
                id=menu_item_id,
                poi_id=request.poi_id,
                name=request.name,
                price=request.price,
            )
        )

    def delete(self, menu_item_id: str) -> bool:
        return self.menu_item_repository.delete(menu_item_id)
