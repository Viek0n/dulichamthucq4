from app.infrastructure.database.mongo import get_database
from app.modules.menu.application.services.menu_item_service import MenuItemService
from app.modules.menu.infrastructure.repositories.mongo_menu_item_repository import (
    MongoMenuItemRepository,
)
from app.modules.poi.application.services.poi_service import POIService
from app.modules.poi.infrastructure.persistence.mongo_poi_repository import (
    MongoPOIRepository,
)


def get_menu_item_service() -> MenuItemService:
    database = get_database()
    collection = database["menu_items"]
    repository = MongoMenuItemRepository(collection)
    return MenuItemService(repository)


def get_poi_service() -> POIService:
    database = get_database()
    poi_repository = MongoPOIRepository(database["POI"])
    menu_item_repository = MongoMenuItemRepository(database["MenuItem"])
    return POIService(poi_repository, menu_item_repository)
