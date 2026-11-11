from bson import ObjectId
from pymongo.collection import Collection

from app.modules.registration.domain.entities.registration import Registration
from app.modules.registration.domain.enumerators.registration_status import (
    RegistrationStatus,
)
from app.modules.registration.domain.exceptions.registration_exceptions import (
    InvalidRegistrationTransition,
    RegistrationNotFound,
)
from app.modules.registration.domain.repositories.registration_repository import (
    RegistrationRepository,
)
from app.modules.registration.infrastructure.persistence.registration_document_mapper import (
    to_document,
    to_domain,
)


class MongoRegistrationRepository(RegistrationRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, registration: Registration) -> Registration:
        document = to_document(registration)
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return to_domain(document)

    def get_by_id(self, registration_id: str) -> Registration | None:
        if not ObjectId.is_valid(registration_id):
            return None
        document = self.collection.find_one({"_id": ObjectId(registration_id)})
        return to_domain(document) if document else None

    def get_by_sender_id(self, sender_id: str) -> list[Registration]:
        if not ObjectId.is_valid(sender_id):
            return []
        documents = self.collection.find({"sender_id": ObjectId(sender_id)})
        return [to_domain(document) for document in documents]

    def get_all(self) -> list[Registration]:
        return [to_domain(document) for document in self.collection.find()]

    def update(self, registration: Registration) -> Registration:
        if registration.id is None or not ObjectId.is_valid(registration.id):
            raise RegistrationNotFound("Registration not found")
        result = self.collection.update_one(
            {
                "_id": ObjectId(registration.id),
                "status": RegistrationStatus.PENDING.value,
            },
            {"$set": to_document(registration)},
        )
        if result.matched_count == 0:
            existing = self.collection.find_one({"_id": ObjectId(registration.id)})
            if existing is None:
                raise RegistrationNotFound("Registration not found")
            raise InvalidRegistrationTransition(
                "Registration has already been reviewed"
            )
        updated = self.collection.find_one({"_id": ObjectId(registration.id)})
        if updated is None:
            raise RegistrationNotFound("Registration not found after update")
        return to_domain(updated)

    def delete(self, registration_id: str) -> bool:
        if not ObjectId.is_valid(registration_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(registration_id)})
        return result.deleted_count > 0

    def delete_pending(self, registration_id: str, sender_id: str) -> bool:
        if not ObjectId.is_valid(registration_id) or not ObjectId.is_valid(sender_id):
            return False
        result = self.collection.delete_one(
            {
                "_id": ObjectId(registration_id),
                "sender_id": ObjectId(sender_id),
                "status": RegistrationStatus.PENDING.value,
            }
        )
        return result.deleted_count > 0
