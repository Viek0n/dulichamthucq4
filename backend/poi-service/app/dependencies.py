from app.application.use_cases.create_poi import CreatePOI
from app.infrastructure.data.repositories.mongo_poi_repository import (
    MongoPOIRepository,
)


def get_create_poi_use_case() -> CreatePOI:
    repository = MongoPOIRepository()
    return CreatePOI(repository)