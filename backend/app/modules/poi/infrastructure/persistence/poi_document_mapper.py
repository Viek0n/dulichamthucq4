from bson import ObjectId

from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.domain.value_objects.coordinate import Coordinate
from app.modules.poi.domain.value_objects.at_time import AtTime


def to_domain(document: dict) -> POI:
    coordinates = document["position"]["coordinates"]

    return POI(
        id=str(document["_id"]),
        name=document["name"],
        address=document["address"],
        open_at=AtTime(document["open_at"]),
        close_at=AtTime(document["close_at"]),
        contact=document["contact"],
        description=document["description"],
        image=document["image"],
        position=Coordinate(
            latitude=coordinates[0],
            longitude=coordinates[1]
        ),
        trigger_radius=document["trigger_radius"],
        is_delete=document["is_delete"],
        poi_owner_id=str(document["poi_owner_id"])
    )


def to_document(poi: POI) -> dict:
    document = {
        "name": poi.name,
        "address": poi.address,
        "open_at": str(poi.open_at.time),
        "close_at": str(poi.close_at.time),
        "contact": poi.contact,
        "description": poi.description,
        "image": poi.image,
        "position": {
            "type": "Point",
            "coordinates": [
                poi.position.latitude,
                poi.position.longitude
            ]
        },
        "trigger_radius": poi.trigger_radius,
        "is_delete": poi.is_delete,
        "poi_owner_id": ObjectId(poi.poi_owner_id)
    }

    if poi.id:
        document["_id"] = ObjectId(poi.id)

    return document