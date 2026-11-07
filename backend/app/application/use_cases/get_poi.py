from app.domain.repositories.poi_repository import POIRepository
from app.domain.entities.poi import POI

class GetPOI:
    def __init__(self, repository: POIRepository):
        self.repository = repository

    def execute(self, slug: str) -> POI:
        return self.repository.get_by_slug(slug)
