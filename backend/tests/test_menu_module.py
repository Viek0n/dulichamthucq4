from unittest.mock import MagicMock

from app.modules.menu.domain.entities.menu_item import MenuItem
from app.modules.menu.infrastructure.repositories.mongo_menu_item_repository import (
    MongoMenuItemRepository,
)
from app.modules.poi.application.services.poi_service import POIService
from bson import ObjectId


def test_menu_item_repository_maps_object_ids_and_supports_poi_cascade():
    poi_id = ObjectId()
    menu_item_id = ObjectId()
    collection = MagicMock()
    collection.insert_one.return_value.inserted_id = menu_item_id
    collection.find.return_value = [
        {
            "_id": menu_item_id,
            "poi_id": poi_id,
            "name": "Bun bo",
            "price": 45000,
        }
    ]
    collection.delete_many.return_value.deleted_count = 1
    repository = MongoMenuItemRepository(collection)

    created = repository.create(
        MenuItem(id=None, poi_id=str(poi_id), name="Bun bo", price=45000)
    )
    found = repository.get_by_poi_id(str(poi_id))
    deleted_count = repository.delete_by_poi_id(str(poi_id))

    assert created == MenuItem(
        id=str(menu_item_id),
        poi_id=str(poi_id),
        name="Bun bo",
        price=45000,
    )
    assert found == [created]
    collection.find.assert_called_once_with({"poi_id": poi_id})
    collection.delete_many.assert_called_once_with({"poi_id": poi_id})
    assert deleted_count == 1


def test_poi_delete_cascades_to_menu_items_only_after_poi_deletion():
    poi_id = str(ObjectId())
    poi_repository = MagicMock()
    menu_item_repository = MagicMock()
    service = POIService(poi_repository, menu_item_repository)

    poi_repository.soft_delete.return_value = True
    assert service.delete(poi_id) is True
    menu_item_repository.delete_by_poi_id.assert_called_once_with(poi_id)

    poi_repository.soft_delete.return_value = False
    menu_item_repository.reset_mock()
    assert service.delete(poi_id) is False
    menu_item_repository.delete_by_poi_id.assert_not_called()
