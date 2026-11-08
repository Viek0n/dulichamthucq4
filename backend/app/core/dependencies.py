from fastapi import Depends
from pymongo.database import Database

from backend.app.modules.poi.infrastructure.data.mongo import get_database
from backend.app.modules.poi.infrastructure.data.repositories.mongo_poi_repository import (
    MongoPOIRepository,
)

def get_poi_repository(
    database: Database = Depends(get_database),
) -> MongoPOIRepository:
    return MongoPOIRepository(database["POI"])