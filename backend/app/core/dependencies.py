from fastapi import Depends
from pymongo.database import Database

from app.infrastructure.database.mongo import get_database
from app.modules.poi.infrastructure.persistence.mongo_poi_repository import (
    MongoPOIRepository,
)

def get_poi_repository(
    database: Database = Depends(get_database),
) -> MongoPOIRepository:
    return MongoPOIRepository(database["POI"])