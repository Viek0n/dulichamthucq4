from app.modules.menu.domain.repositories.menu_item_repository import MenuItemRepository
from app.modules.poi.application.dto.poi_create_request import POICreateRequest
from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.domain.repositories.poi_repository import POIRepository
from app.modules.poi.domain.value_objects.at_time import AtTime
from app.modules.poi.domain.value_objects.coordinate import Coordinate
from app.modules.poi.infrastructure.exceptions.poi_exceptions import POINotFound


class POIService:
    def __init__(
        self,
        poi_repository: POIRepository,
        menu_item_repository: MenuItemRepository,
    ):
        self.poi_repository = poi_repository
        self.menu_item_repository = menu_item_repository

    def create(self, request: POICreateRequest, owner_id: str) -> POI:
        existing_poi = self.poi_repository.get_by_slug(request.slug)

        if existing_poi:
            raise ValueError("POI slug already exists")

        return self.poi_repository.create(
            self._to_poi(request, poi_id=None, owner_id=owner_id)
        )

    def get_by_id(self, poi_id: str) -> POI | None:
        return self.poi_repository.get_by_id(poi_id)

    def get_by_slug(self, slug: str) -> POI | None:
        return self.poi_repository.get_by_slug(slug)

    def get_all(self) -> list[POI]:
        return self.poi_repository.get_all()

    def update(self, poi_id: str, request: POICreateRequest) -> POI:
        existing_poi = self.poi_repository.get_by_id(poi_id)
        if existing_poi is None:
            raise POINotFound("Không tìm thấy")

        slug_owner = self.poi_repository.get_by_slug(request.slug)
        if slug_owner is not None and slug_owner.id != poi_id:
            raise ValueError("POI slug already exists")

        poi = self._to_poi(
            request,
            poi_id=existing_poi.id,
            owner_id=existing_poi.poi_owner_id,
        )
        return self.poi_repository.update(poi)

    def delete(self, poi_id: str) -> bool:
        if not self.poi_repository.soft_delete(poi_id):
            return False

        self.menu_item_repository.delete_by_poi_id(poi_id)
        return True

    @staticmethod
    def _to_poi(
        request: POICreateRequest,
        poi_id: str | None,
        owner_id: str,
    ) -> POI:
        return POI(
            id=poi_id,
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
