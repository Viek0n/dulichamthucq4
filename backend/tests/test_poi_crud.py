from unittest.mock import MagicMock

import pytest
from app.modules.menu.domain.repositories.menu_item_repository import (
    MenuItemRepository,
)
from app.modules.poi.application.services.poi_service import POIService
from app.modules.poi.domain.entities.poi import POI
from app.modules.poi.domain.value_objects.at_time import AtTime
from app.modules.poi.domain.value_objects.coordinate import Coordinate
from app.modules.poi.infrastructure.exceptions.poi_exceptions import POINotFound
from app.modules.poi.infrastructure.persistence.mongo_poi_repository import (
    MongoPOIRepository,
)
from app.modules.poi.presentation.schemas.poi_create_request import POICreateRequest
from bson import ObjectId


def _poi_document(poi_id: ObjectId) -> dict:
    return {
        "_id": poi_id,
        "name": "Old name",
        "address": "Old address",
        "open_at": "08:00",
        "close_at": "17:00",
        "contact": "123",
        "description": "",
        "image": "",
        "position": {"type": "Point", "coordinates": [10.0, 106.0]},
        "trigger_radius": 50,
        "is_delete": False,
        "poi_owner_id": ObjectId(),
    }


def test_poi_repository_reads_active_records_and_returns_updated_entity():
    poi_id = ObjectId()
    document = _poi_document(poi_id)
    collection = MagicMock()
    collection.find_one.return_value = document
    collection.find.return_value = [document]
    collection.update_one.return_value.matched_count = 1
    repository = MongoPOIRepository(collection)

    assert repository.get_by_id(str(poi_id)).id == str(poi_id)
    assert repository.get_all()[0].id == str(poi_id)

    poi = POI(
        id=str(poi_id),
        name="New name",
        address="New address",
        open_at=AtTime("09:00"),
        close_at=AtTime("18:00"),
        contact="456",
        description="Updated",
        image="new.png",
        position=Coordinate(latitude=11, longitude=107),
        trigger_radius=75,
        poi_owner_id=str(document["poi_owner_id"]),
    )
    updated_document = {**document, "name": poi.name}
    collection.find_one.return_value = updated_document
    updated = repository.update(poi)

    assert updated.name == "New name"
    collection.update_one.assert_called_once()


def test_poi_repository_rejects_update_for_unknown_or_deleted_poi():
    collection = MagicMock()
    collection.update_one.return_value.matched_count = 0
    repository = MongoPOIRepository(collection)
    poi = POI(
        id=str(ObjectId()),
        name="Name",
        address="Address",
        open_at=AtTime("09:00"),
        close_at=AtTime("18:00"),
        contact="456",
        description="",
        image="",
        position=Coordinate(latitude=11, longitude=107),
        poi_owner_id=str(ObjectId()),
    )

    try:
        repository.update(poi)
    except POINotFound:
        pass
    else:
        raise AssertionError("Expected missing POI update to fail")


def test_poi_repository_soft_deletes_only_valid_active_ids():
    poi_id = str(ObjectId())
    collection = MagicMock()
    collection.update_one.return_value.modified_count = 1
    repository = MongoPOIRepository(collection)

    assert repository.soft_delete(poi_id) is True
    collection.update_one.assert_called_once_with(
        {"_id": ObjectId(poi_id), "is_delete": False},
        {"$set": {"is_delete": True}},
    )
    assert repository.soft_delete("invalid-id") is False


def test_poi_service_updates_existing_poi_and_preserves_owner():
    poi_id = str(ObjectId())
    owner_id = str(ObjectId())
    existing_poi = POI(
        id=poi_id,
        name="Old name",
        address="Old address",
        open_at=AtTime("08:00"),
        close_at=AtTime("17:00"),
        contact="123",
        description="",
        image="",
        position=Coordinate(latitude=10, longitude=106),
        poi_owner_id=owner_id,
    )
    poi_repository = MagicMock()
    poi_repository.get_by_id.return_value = existing_poi
    poi_repository.update.side_effect = lambda poi: poi
    service = POIService(
        poi_repository,
        MagicMock(spec=MenuItemRepository),
    )
    request = POICreateRequest(
        name="New name",
        address="New address",
        open_at="09:00",
        close_at="18:00",
        contact="456",
        latitude=11,
        longitude=107,
    )

    updated = service.update(poi_id, request)

    assert updated.id == poi_id
    assert updated.poi_owner_id == owner_id
    poi_repository.update.assert_called_once_with(updated)
