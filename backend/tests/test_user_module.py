from unittest.mock import MagicMock, call

import pytest
from bson import ObjectId
from cryptography.fernet import Fernet

from app.modules.role.domain.entities.role import Role
from app.modules.user.application.dto.auth_requests import ChangePasswordRequest
from app.modules.user.application.dto.user_create_request import (
    UserCreateRequest,
    UserUpdateRequest,
)
from app.modules.user.application.services.user_service import UserService
from app.modules.user.domain.entities.user import User, UserStatus
from app.modules.user.domain.exceptions.user_exceptions import UserAlreadyExists
from app.modules.user.infrastructure.persistence.mongo_user_repository import (
    MongoUserRepository,
)
from app.modules.user.infrastructure.persistence.user_document_mapper import (
    to_document,
    to_domain,
)
from app.modules.user.infrastructure.security.user_security import UserSecurity
from app.modules.user.presentation.controllers.auth_controller import (
    router as auth_router,
)
from app.modules.user.presentation.controllers.user_controller import (
    UserLoginRequest,
    login,
)


def _security() -> UserSecurity:
    return UserSecurity(
        encryption_key=Fernet.generate_key().decode("ascii"),
        lookup_hmac_key="l" * 32,
        jwt_secret_key="j" * 32,
        jwt_expiration_minutes=30,
    )


def _create_request(role_id: str) -> UserCreateRequest:
    return UserCreateRequest(
        password="a-strong-password",
        is_poi_owner_verified=False,
        name="Test User",
        email="Test@Example.com",
        phone="+1 555 0100",
        role_id=role_id,
    )


def test_security_hashes_password_encrypts_contacts_and_signs_jwt():
    security = _security()
    password_hash = security.hash_password("correct horse battery")

    assert password_hash != "correct horse battery"
    assert security.verify_password("correct horse battery", password_hash)
    assert not security.verify_password("wrong password", password_hash)

    encrypted = security.encrypt("user@example.com")
    assert encrypted != "user@example.com"
    assert security.decrypt(encrypted) == "user@example.com"
    assert security.lookup_hash("Test@Example.com", "email") == security.lookup_hash(
        "test@example.com", "email"
    )
    assert security.lookup_hash("test@example.com", "email") != security.lookup_hash(
        "test@example.com", "phone"
    )

    token = security.create_access_token(str(ObjectId()))
    assert security.decode_access_token(token)


def test_user_document_maps_required_schema_fields():
    user_id = ObjectId()
    role_id = ObjectId()
    document = {
        "_id": user_id,
        "password_hash": "bcrypt-hash",
        "is_poi_owner_verified": False,
        "status": "ACTIVE",
        "name": "Test User",
        "email_encrypted": "encrypted-email",
        "email_hash": "email-hash",
        "phone_encrypted": "encrypted-phone",
        "phone_hash": "phone-hash",
        "role_id": role_id,
    }

    user = to_domain(document)
    assert user == User(
        id=str(user_id),
        password_hash="bcrypt-hash",
        is_poi_owner_verified=False,
        status=UserStatus.ACTIVE,
        name="Test User",
        email_encrypted="encrypted-email",
        email_hash="email-hash",
        phone_encrypted="encrypted-phone",
        phone_hash="phone-hash",
        role_id=str(role_id),
    )
    assert to_document(user) == {
        key: value for key, value in document.items() if key != "_id"
    }


def test_user_repository_reads_active_users_and_soft_deletes():
    user_id = ObjectId()
    role_id = ObjectId()
    document = {
        "_id": user_id,
        "password_hash": "bcrypt-hash",
        "is_poi_owner_verified": False,
        "status": "ACTIVE",
        "name": "Test User",
        "email_encrypted": "encrypted-email",
        "email_hash": "email-hash",
        "phone_encrypted": "encrypted-phone",
        "phone_hash": "phone-hash",
        "role_id": role_id,
    }
    collection = MagicMock()
    collection.find_one.return_value = document
    collection.find.return_value = [document]
    collection.update_one.return_value.modified_count = 1
    repository = MongoUserRepository(collection)

    assert repository.get_by_id(str(user_id)).id == str(user_id)
    assert repository.get_by_email_hash("email-hash").id == str(user_id)
    assert repository.get_by_phone_hash("phone-hash").id == str(user_id)
    assert repository.get_all()[0].id == str(user_id)
    assert repository.soft_delete(str(user_id))
    assert repository.soft_delete("invalid-id") is False
    collection.update_one.assert_called_once_with(
        {
            "_id": user_id,
            "status": {"$ne": UserStatus.SOFT_DELETE.value},
        },
        {"$set": {"status": UserStatus.SOFT_DELETE.value}},
    )


def test_user_service_create_encrypts_contacts_and_preserves_no_plaintext():
    role_id = str(ObjectId())
    user_repository = MagicMock()
    user_repository.get_by_email_hash.return_value = None
    user_repository.get_by_phone_hash.return_value = None
    role_repository = MagicMock()
    role_repository.get_by_id.return_value = Role(
        id=role_id,
        name="Admin",
        permissions=["user.create"],
        priority=10,
    )
    user_repository.create.side_effect = lambda user: User(
        **{**user.__dict__, "id": str(ObjectId())}
    )
    security = _security()
    service = UserService(user_repository, role_repository, security)

    created = service.create(_create_request(role_id))

    user_repository.create.assert_called_once()
    stored = user_repository.create.call_args.args[0]
    assert created.password_hash != "a-strong-password"
    assert stored.email_encrypted != "Test@example.com"
    assert stored.phone_encrypted != "+1 555 0100"
    assert "password_hash" not in service.to_response_data(created)
    assert service.to_response_data(created)["email"] == "test@example.com"


def test_user_service_authenticates_only_active_users():
    role_id = str(ObjectId())
    user_repository = MagicMock()
    security = _security()
    user = User(
        id=str(ObjectId()),
        password_hash=security.hash_password("a-strong-password"),
        is_poi_owner_verified=False,
        status=UserStatus.ACTIVE,
        name="Test User",
        email_encrypted=security.encrypt("test@example.com"),
        email_hash="email-hash",
        phone_encrypted=security.encrypt("+1 555 0100"),
        phone_hash="phone-hash",
        role_id=role_id,
    )
    user_repository.get_by_email_hash.return_value = user
    user_repository.get_by_phone_hash.return_value = user
    service = UserService(user_repository, MagicMock(), security)

    assert service.authenticate("Test@Example.com", "a-strong-password") == user
    assert service.authenticate("+1 555 0100", "a-strong-password") == user
    assert service.authenticate("test@example.com", "wrong-password") is None

    user_repository.get_by_email_hash.assert_called_with(
        security.lookup_hash("test@example.com", "email")
    )
    user_repository.get_by_phone_hash.assert_called_with(
        security.lookup_hash("+1 555 0100", "phone")
    )

    inactive_user = User(
        **{**user.__dict__, "status": UserStatus.INACTIVE}
    )
    user_repository.get_by_email_hash.return_value = inactive_user
    user_repository.get_by_phone_hash.return_value = inactive_user
    assert service.authenticate("test@example.com", "a-strong-password") is None
    assert service.authenticate("+1 555 0100", "a-strong-password") is None


def test_user_service_changes_password_only_after_current_password_verifies():
    security = _security()
    user = User(
        id=str(ObjectId()),
        password_hash=security.hash_password("old-password"),
        is_poi_owner_verified=False,
        status=UserStatus.ACTIVE,
        name="Test User",
        email_encrypted=security.encrypt("test@example.com"),
        email_hash="email-hash",
        phone_encrypted=security.encrypt("+1 555 0100"),
        phone_hash="phone-hash",
        role_id=str(ObjectId()),
    )
    repository = MagicMock()
    repository.get_by_id.return_value = user
    service = UserService(repository, MagicMock(), security)

    with pytest.raises(ValueError, match="Current password is incorrect"):
        service.change_password(user.id, "wrong-password", "new-password")
    repository.update.assert_not_called()

    assert service.change_password(user.id, "old-password", "new-password")
    repository.update.assert_called_once_with(user)
    assert security.verify_password("new-password", user.password_hash)
    assert not security.verify_password("old-password", user.password_hash)


def test_change_password_request_validates_new_password_length():
    assert ChangePasswordRequest(
        current_password="old-password",
        new_password="new-password",
    ).new_password == "new-password"
    with pytest.raises(ValueError, match="at least 8 characters"):
        ChangePasswordRequest(
            current_password="old-password",
            new_password="short",
        )
    with pytest.raises(ValueError, match="72 UTF-8 bytes"):
        ChangePasswordRequest(
            current_password="old-password",
            new_password="é" * 40,
        )


def test_admin_auth_routes_are_registered():
    assert {(route.path, tuple(route.methods)) for route in auth_router.routes} == {
        ("/admin/auth/me", ("GET",)),
        ("/admin/auth/change-password", ("POST",)),
    }


def test_user_login_request_accepts_email_or_phone_in_identifier_field():
    assert UserLoginRequest(
        identifier=" Test@Example.com ", password="correct-horse"
    ).identifier == "test@example.com"
    assert UserLoginRequest(
        identifier=" +1 555 0100 ", password="correct-horse"
    ).identifier == (
        "+1 555 0100"
    )

    with pytest.raises(ValueError, match="Field required"):
        UserLoginRequest(password="correct-horse")
    with pytest.raises(ValueError, match="Invalid email address"):
        UserLoginRequest(identifier="user@invalid", password="correct-horse")
    with pytest.raises(ValueError, match="32 characters"):
        UserLoginRequest(identifier="1" * 33, password="correct-horse")
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        UserLoginRequest(legacy_field="value", password="correct-horse")


def test_login_controller_authenticates_email_or_phone_identifier():
    service = MagicMock()
    service.authenticate.return_value = MagicMock(id=str(ObjectId()))
    service.security.create_access_token.return_value = "access-token"

    for request in (
        UserLoginRequest(identifier="user@example.com", password="correct-horse"),
        UserLoginRequest(identifier="+1 555 0100", password="correct-horse"),
    ):
        response = login(request, service)

        assert response.access_token == "access-token"
    service.authenticate.assert_has_calls(
        [
            call("user@example.com", "correct-horse"),
            call("+1 555 0100", "correct-horse"),
        ]
    )


def test_user_service_rejects_duplicate_contact_and_missing_role():
    role_id = str(ObjectId())
    user_repository = MagicMock()
    role_repository = MagicMock()
    service = UserService(user_repository, role_repository, _security())
    user_repository.get_by_email_hash.return_value = None
    user_repository.get_by_phone_hash.return_value = None

    user_repository.get_by_email_hash.return_value = User(
        id=str(ObjectId()),
        password_hash="hash",
        is_poi_owner_verified=False,
        status=UserStatus.ACTIVE,
        name="Existing",
        email_encrypted="encrypted",
        email_hash="hash",
        phone_encrypted="encrypted",
        phone_hash="hash",
        role_id=role_id,
    )
    with pytest.raises(UserAlreadyExists, match="Email already exists"):
        service.create(_create_request(role_id))

    user_repository.get_by_email_hash.return_value = None
    user_repository.get_by_phone_hash.return_value = None
    role_repository.get_by_id.return_value = None
    with pytest.raises(ValueError, match="Role not found"):
        service.create(_create_request(role_id))


def test_user_update_omitting_password_keeps_existing_hash():
    user_id = str(ObjectId())
    role_id = str(ObjectId())
    security = _security()
    existing = User(
        id=user_id,
        password_hash="existing-bcrypt-hash",
        is_poi_owner_verified=False,
        status=UserStatus.ACTIVE,
        name="Test User",
        email_encrypted=security.encrypt("test@example.com"),
        email_hash=security.lookup_hash("test@example.com", "email"),
        phone_encrypted=security.encrypt("+1 555 0100"),
        phone_hash=security.lookup_hash("+1 555 0100", "phone"),
        role_id=role_id,
    )
    user_repository = MagicMock()
    user_repository.get_by_id.return_value = existing
    user_repository.get_by_email_hash.return_value = existing
    user_repository.get_by_phone_hash.return_value = existing
    user_repository.update.side_effect = lambda user: user
    role_repository = MagicMock()
    role_repository.get_by_id.return_value = Role(
        id=role_id,
        name="Role",
        permissions=["user.update"],
        priority=1,
    )
    request = UserUpdateRequest(
        is_poi_owner_verified=True,
        status=UserStatus.ACTIVE,
        name="Updated User",
        email="test@example.com",
        phone="+1 555 0100",
        role_id=role_id,
    )
    service = UserService(user_repository, role_repository, security)

    updated = service.update(user_id, request)

    assert updated.password_hash == "existing-bcrypt-hash"
    assert updated.is_poi_owner_verified is True
    assert updated.name == "Updated User"


def test_user_request_rejects_invalid_email_soft_delete_and_oversized_password():
    with pytest.raises(ValueError, match="Invalid email address"):
        UserCreateRequest(
            password="a-strong-password",
            name="Test User",
            email="not-an-email",
            phone="+1 555 0100",
            role_id=str(ObjectId()),
        )

    with pytest.raises(ValueError, match="soft-delete"):
        UserCreateRequest(
            password="a-strong-password",
            status=UserStatus.SOFT_DELETE,
            name="Test User",
            email="test@example.com",
            phone="+1 555 0100",
            role_id=str(ObjectId()),
        )

    with pytest.raises(ValueError, match="72 UTF-8 bytes"):
        UserCreateRequest(
            password="é" * 40,
            name="Test User",
            email="test@example.com",
            phone="+1 555 0100",
            role_id=str(ObjectId()),
        )
