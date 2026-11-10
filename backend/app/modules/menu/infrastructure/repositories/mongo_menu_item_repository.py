from app.modules.menu.domain.entities.menu_item import MenuItem
from app.modules.menu.domain.repositories.menu_item_repository import MenuItemRepository
from app.modules.menu.infrastructure.exceptions.menu_item_exceptions import (
    MenuItemNotFound,
)
from bson import ObjectId
from pymongo.collection import Collection


class MongoMenuItemRepository(MenuItemRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, menu_item: MenuItem) -> MenuItem:
        if not ObjectId.is_valid(menu_item.poi_id):
            raise ValueError("Invalid POI id")

        document = {
            "poi_id": ObjectId(menu_item.poi_id),
            "name": menu_item.name,
            "price": menu_item.price,
        }
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return self._to_entity(document)

    def get_by_id(self, menu_item_id: str) -> MenuItem | None:
        if not ObjectId.is_valid(menu_item_id):
            return None

        document = self.collection.find_one({"_id": ObjectId(menu_item_id)})
        return self._to_entity(document) if document else None

    def get_by_poi_id(self, poi_id: str) -> list[MenuItem]:
        if not ObjectId.is_valid(poi_id):
            return []

        documents = self.collection.find({"poi_id": ObjectId(poi_id)})
        return [self._to_entity(document) for document in documents]

    def update(self, menu_item: MenuItem) -> MenuItem:
        if not menu_item.id or not ObjectId.is_valid(menu_item.id):
            raise MenuItemNotFound("Menu item not found")
        if not ObjectId.is_valid(menu_item.poi_id):
            raise ValueError("Invalid POI id")

        result = self.collection.update_one(
            {"_id": ObjectId(menu_item.id)},
            {
                "$set": {
                    "poi_id": ObjectId(menu_item.poi_id),
                    "name": menu_item.name,
                    "price": menu_item.price,
                }
            },
        )
        if result.matched_count == 0:
            raise MenuItemNotFound("Menu item not found")

        updated = self.collection.find_one({"_id": ObjectId(menu_item.id)})
        if updated is None:
            raise MenuItemNotFound("Menu item not found after update")
        return self._to_entity(updated)

    def delete(self, menu_item_id: str) -> bool:
        if not ObjectId.is_valid(menu_item_id):
            return False

        result = self.collection.delete_one({"_id": ObjectId(menu_item_id)})
        return result.deleted_count > 0

    def delete_by_poi_id(self, poi_id: str) -> int:
        if not ObjectId.is_valid(poi_id):
            raise ValueError("Invalid POI id")

        result = self.collection.delete_many({"poi_id": ObjectId(poi_id)})
        return result.deleted_count

    @staticmethod
    def _to_entity(document: dict) -> MenuItem:
        return MenuItem(
            id=str(document["_id"]),
            poi_id=str(document["poi_id"]),
            name=document["name"],
            price=document["price"],
        )
