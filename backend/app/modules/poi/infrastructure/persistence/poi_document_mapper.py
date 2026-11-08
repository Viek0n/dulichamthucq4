from bson import ObjectId

from modules.poi.domain.entities.poi import POI


def to_domain(document: dict) -> POI:
    return POI(
        id=str(document["_id"]),
        slug=document["slug"],
        name=document["name"],
        latitude=document["latitude"],
        longitude=document["longitude"],
        trigger_radius=document["trigger_radius"],
        is_delete=document["is_delete"],
    )


def to_document(poi: POI) -> dict:
    document = {
        "slug": poi.slug,
        "name": poi.name,
        "latitude": poi.latitude,
        "longitude": poi.longitude,
        "trigger_radius": poi.trigger_radius,
        "is_delete": poi.is_delete,
    }

    if poi.id:
        document["_id"] = ObjectId(poi.id)

    return document