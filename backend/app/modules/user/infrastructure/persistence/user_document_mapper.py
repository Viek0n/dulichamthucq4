from bson import ObjectId

from app.modules.user.domain.entities.user import User, UserStatus


def to_domain(document: dict) -> User:
    return User(
        id=str(document["_id"]),
        password_hash=document["password_hash"],
        is_poi_owner_verified=document["is_poi_owner_verified"],
        status=UserStatus(document["status"]),
        name=document["name"],
        email_encrypted=document["email_encrypted"],
        email_hash=document["email_hash"],
        phone_encrypted=document["phone_encrypted"],
        phone_hash=document["phone_hash"],
        role_id=str(document["role_id"]),
    )


def to_document(user: User) -> dict:
    return {
        "password_hash": user.password_hash,
        "is_poi_owner_verified": user.is_poi_owner_verified,
        "status": user.status.value,
        "name": user.name,
        "email_encrypted": user.email_encrypted,
        "email_hash": user.email_hash,
        "phone_encrypted": user.phone_encrypted,
        "phone_hash": user.phone_hash,
        "role_id": ObjectId(user.role_id),
    }
