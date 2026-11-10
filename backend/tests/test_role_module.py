from unittest.mock import MagicMock

import pytest
from app.modules.role.application.dto.role_create_request import RoleCreateRequest
from app.modules.role.application.services.role_service import RoleService
from app.modules.role.domain.entities.role import Role
from app.modules.role.infrastructure.exceptions.role_exceptions import RoleNotFound
from app.modules.role.infrastructure.persistence.mongo_role_repository import (
    MongoRoleRepository,
)
from bson import ObjectId


def test_role_repository_round_trips_role_and_uses_object_id():
    role_id = ObjectId()
    collection = MagicMock()
    collection.insert_one.return_value.inserted_id = role_id
    collection.find_one.return_value = {
        "_id": role_id,
        "name": "Store owner",
        "permissions": ["poi.create", "poi.update"],
        "priority": 10,
    }
    repository = MongoRoleRepository(collection)

    created = repository.create(
        Role(
            id=None,
            name="Store owner",
            permissions=["poi.create", "poi.update"],
            priority=10,
        )
    )
    found = repository.get_by_id(str(role_id))

    assert created == Role(
        id=str(role_id),
        name="Store owner",
        permissions=["poi.create", "poi.update"],
        priority=10,
    )
    assert found == created
    assert collection.find_one.call_args.args[0] == {"_id": role_id}


def test_role_repository_updates_and_deletes_role():
    role_id = ObjectId()
    collection = MagicMock()
    collection.update_one.return_value.matched_count = 1
    collection.find_one.return_value = {
        "_id": role_id,
        "name": "Administrator",
        "permissions": ["user.create"],
        "priority": 100,
    }
    collection.delete_one.return_value.deleted_count = 1
    repository = MongoRoleRepository(collection)
    role = Role(
        id=str(role_id),
        name="Administrator",
        permissions=["user.create"],
        priority=100,
    )

    assert repository.update(role) == role
    collection.update_one.assert_called_once_with(
        {"_id": role_id},
        {
            "$set": {
                "name": "Administrator",
                "permissions": ["user.create"],
                "priority": 100,
            }
        },
    )
    assert repository.delete(str(role_id)) is True
    assert repository.delete("invalid-id") is False


def test_role_repository_raises_not_found_for_missing_update():
    collection = MagicMock()
    collection.update_one.return_value.matched_count = 0
    repository = MongoRoleRepository(collection)

    with pytest.raises(RoleNotFound):
        repository.update(
            Role(
                id=str(ObjectId()),
                name="Administrator",
                permissions=[],
                priority=100,
            )
        )


def test_role_request_accepts_only_the_fixed_permission_catalog():
    request = RoleCreateRequest(
        name="Store owner",
        permissions=[
            "poi.read",
            "poi.approve",
            "analytics.view_own",
            "owner.manage_own_poi",
            "content.publish",
        ],
        priority=10,
    )
    assert request.permissions == [
        "poi.read",
        "poi.approve",
        "analytics.view_own",
        "owner.manage_own_poi",
        "content.publish",
    ]

    with pytest.raises(ValueError, match="Unknown permissions: POI_CREATE"):
        RoleCreateRequest(
            name="Invalid",
            permissions=["POI_CREATE"],
            priority=0,
        )

    with pytest.raises(ValueError, match="must not contain duplicates"):
        RoleCreateRequest(
            name="Duplicate",
            permissions=["role.read", "role.read"],
            priority=0,
        )


def test_permission_catalog_contains_every_professor_listed_value():
    from app.modules.role.domain.enumerators.permissions.permission_catalog import (
        ALL_PERMISSIONS,
    )

    assert ALL_PERMISSIONS == {
        "poi.read",
        "poi.create",
        "poi.update",
        "poi.delete",
        "poi.approve",
        "poi.toggle",
        "menu.read",
        "menu.create",
        "menu.update",
        "menu.delete",
        "user.read",
        "user.create",
        "user.update",
        "user.delete",
        "role.read",
        "role.create",
        "role.update",
        "role.delete",
        "analytics.view",
        "analytics.export",
        "analytics.view_own",
        "audit.read",
        "audit.manage",
        "system.config",
        "system.logs",
        "system.backup",
        "owner.register",
        "owner.access",
        "owner.submit_poi",
        "owner.manage_own_poi",
        "content.moderate",
        "content.publish",
    }
