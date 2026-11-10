from bson import ObjectId
from pymongo.collection import Collection

from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.domain.repositories.poi_repository import POIRepository
from app.modules.poi.infrastructure.persistence.poi_document_mapper import *
from app.modules.poi.infrastructure.exceptions.poi_exceptions import *


class MongoPOIRepository(POIRepository):

    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, poi: POI) -> POI:
        document = to_document(poi)

        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id

        return to_domain(document)

    def get_by_id(self, poi_id: str) -> POI | None:
        if not ObjectId.is_valid(poi_id):
            return None

        document = self.collection.find_one({
            "_id": ObjectId(poi_id),
            "is_delete": False,
        })

        return to_domain(document) if document else None

    def get_by_slug(self, slug: str) -> POI | None:
        document = self.collection.find_one({
            "slug": slug,
            "is_delete": False,
        })

        return to_domain(document) if document else None

    def update(self, poi: POI) -> POI:
        document = to_document(poi)
        document.pop("_id", None)

        result = self.collection.update_one(
            {
                "_id": ObjectId(poi.id)
            },
            {
                "$set": document
            },
        )

        if result.matched_count == 0:
            raise POINotFound("Không tìm thấy")

        updated = self.collection.find_one({"_id": ObjectId(poi.id)})
        return to_domain(self.update)

    def soft_delete(self, poi_id: str) -> bool:
        if not ObjectId.is_valid(poi_id):
            return False

        result = self.collection.update_one(
            {"_id": ObjectId(poi_id), "is_delete": False},
            {"$set": {"is_delete": True}},
        )

        return result.modified_count > 0