from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from app.modules.user.domain.entities.user import User, UserStatus
from app.modules.user.domain.exceptions.user_exceptions import (
    UserAlreadyExists,
    UserNotFound,
)
from app.modules.user.domain.repositories.user_repository import UserRepository
from app.modules.user.infrastructure.persistence.user_document_mapper import (
    to_document,
    to_domain,
)


class MongoUserRepository(UserRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, user: User) -> User:
        document = to_document(user)
        try:
            result = self.collection.insert_one(document)
        except DuplicateKeyError as error:
            raise UserAlreadyExists("Email or phone already exists") from error
        document["_id"] = result.inserted_id
        return to_domain(document)

    def get_by_id(self, user_id: str) -> User | None:
        if not ObjectId.is_valid(user_id):
            return None

        document = self.collection.find_one(
            {"_id": ObjectId(user_id), "status": {"$ne": UserStatus.SOFT_DELETE.value}}
        )
        return to_domain(document) if document else None

    def get_by_email_hash(self, email_hash: str) -> User | None:
        document = self.collection.find_one(
            {
                "email_hash": email_hash,
                "status": {"$ne": UserStatus.SOFT_DELETE.value},
            }
        )
        return to_domain(document) if document else None

    def get_by_phone_hash(self, phone_hash: str) -> User | None:
        document = self.collection.find_one(
            {
                "phone_hash": phone_hash,
                "status": {"$ne": UserStatus.SOFT_DELETE.value},
            }
        )
        return to_domain(document) if document else None

    def get_all(self) -> list[User]:
        documents = self.collection.find(
            {"status": {"$ne": UserStatus.SOFT_DELETE.value}}
        )
        return [to_domain(document) for document in documents]

    def update(self, user: User) -> User:
        if not user.id or not ObjectId.is_valid(user.id):
            raise UserNotFound("User not found")

        try:
            result = self.collection.update_one(
                {
                    "_id": ObjectId(user.id),
                    "status": {"$ne": UserStatus.SOFT_DELETE.value},
                },
                {"$set": to_document(user)},
            )
        except DuplicateKeyError as error:
            raise UserAlreadyExists("Email or phone already exists") from error
        if result.matched_count == 0:
            raise UserNotFound("User not found")

        updated = self.collection.find_one({"_id": ObjectId(user.id)})
        if updated is None:
            raise UserNotFound("User not found after update")
        return to_domain(updated)

    def soft_delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False

        result = self.collection.update_one(
            {
                "_id": ObjectId(user_id),
                "status": {"$ne": UserStatus.SOFT_DELETE.value},
            },
            {"$set": {"status": UserStatus.SOFT_DELETE.value}},
        )
        return result.modified_count > 0
