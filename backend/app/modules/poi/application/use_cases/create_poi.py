from domain.entities.poi import POI
from domain.repositories.poi_repository import POIRepository

class CreatePOI:
    def __init__(self, repository: POIRepository):
        self.repository = repository

    def execute(self, poi:POI) -> POI:
        exsisting_poi = self.repository.get_by_slug(poi.slug)

        if exsisting_poi is not None:
            raise ValueError("POI đã tồn tại")

        return self.repository.create(poi)