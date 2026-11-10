from fastapi import Depends
from pymongo.database import Database

from app.infrastructure.database.mongo import get_database
from app.modules.poi.application.services.poi_service import POIService
from app.modules.poi.infrastructure.persistence.mongo_poi_repository import (
    MongoPOIRepository,
)

def get_poi_service() -> POIService:
    database = get_database()
    collection = database["POI"]

    repository = MongoPOIRepository(collection)
    return POIService(repository)