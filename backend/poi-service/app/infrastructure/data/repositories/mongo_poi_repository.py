from bson import ObjectId

from app.domain.entities.poi import POI
from app.domain.repositories.poi_repository import POIRepository


class MongoPOIRepository(POIRepository):

    def __init__(self, collection):
        self.collection = collection

    def create(self, poi: POI) -> POI:
        document = {
            "slug": poi.slug,
            "name": poi.name,
            "address": poi.address,
            "open_at": poi.open_at,
            "close_at": poi.close_at,
            "contact": poi.contact,
            "image": poi.image,
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "trigger_radius": poi.trigger_radius,
            "is_delete": poi.is_delete,
            "poi_owner_id": ObjectId(poi.poi_owner_id),
        }

        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id

        return self._to_entity(document)

    def get_by_id(self, poi_id: str) -> POI | None:
        if not ObjectId.is_valid(poi_id):
            return None

        document = self.collection.find_one({
            "_id": ObjectId(poi_id),
            "is_delete": False,
        })

        return self._to_entity(document) if document else None

    def get_by_slug(self, slug: str) -> POI | None:
        document = self.collection.find_one({
            "slug": slug,
            "is_delete": False,
        })

        return self._to_entity(document) if document else None

    def update(self, poi: POI) -> POI:
        document = {
            "slug": poi.slug,
            "name": poi.name,
            "address": poi.address,
            "open_at": poi.open_at,
            "close_at": poi.close_at,
            "contact": poi.contact,
            "image": poi.image,
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "trigger_radius": poi.trigger_radius,
            "is_delete": poi.is_delete,
            "poi_owner_id": ObjectId(poi.poi_owner_id),
        }

        result = self.collection.update_one(
            {"_id": ObjectId(poi.id)},
            {"$set": document},
        )

        if result.matched_count == 0:
            raise ValueError("POI not found")

        updated = self.collection.find_one({"_id": ObjectId(poi.id)})
        return self._to_entity(updated)

    def soft_delete(self, poi_id: str) -> bool:
        if not ObjectId.is_valid(poi_id):
            return False

        result = self.collection.update_one(
            {"_id": ObjectId(poi_id), "is_delete": False},
            {"$set": {"is_delete": True}},
        )

        return result.modified_count > 0

    @staticmethod
    def _to_entity(document: dict) -> POI:
        return POI(
            id=str(document["_id"]),
            slug=document["slug"],
            name=document["name"],
            address=document.get("address", ""),
            open_at=document["open_at"],
            close_at=document["close_at"],
            contact=document["contact"],
            image=document["image"],
            latitude=document["latitude"],
            longitude=document["longitude"],
            trigger_radius=document["trigger_radius"],
            is_delete=document["is_delete"],
            poi_owner_id=str(document["poi_owner_id"]),
        )