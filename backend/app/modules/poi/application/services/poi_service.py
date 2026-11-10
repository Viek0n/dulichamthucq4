from app.modules.menu.domain.repositories.menu_item_repository import MenuItemRepository
from app.modules.poi.application.dto.poi_create_request import POICreateRequest
from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.domain.repositories.poi_repository import POIRepository
from app.modules.poi.domain.value_objects.at_time import AtTime
from app.modules.poi.domain.value_objects.coordinate import Coordinate


class POIService:
    def __init__(
        self,
        poi_repository: POIRepository,
        menu_item_repository: MenuItemRepository,
    ):
        self.poi_repository = poi_repository
        self.menu_item_repository = menu_item_repository

    def create(self, request: POICreateRequest, owner_id: str):
        exsisting_poi = self.poi_repository.get_by_slug(request.slug)

        if exsisting_poi:
            raise ValueError("POI slug already exists")

        poi = POI(
            id=None,
            slug=request.slug,
            name=request.name,
            address=request.address,
            open_at=AtTime(request.open_at),
            close_at=AtTime(request.close_at),
            contact=request.contact,
            description=request.description,
            image=request.image,
            position=Coordinate(
                longitude=request.longitude,
                latitude=request.latitude,
            ),
            trigger_radius=request.trigger_radius,
            is_delete=False,
            poi_owner_id=owner_id,
        )

        return self.poi_repository.create(poi)

    def delete(self, poi_id: str) -> bool:
        if not self.poi_repository.soft_delete(poi_id):
            return False

        self.menu_item_repository.delete_by_poi_id(poi_id)
        return True
