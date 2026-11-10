from app.modules.role.domain.entities.role import Role
from app.modules.role.domain.repositories.role_repository import RoleRepository
from app.modules.role.infrastructure.exceptions.role_exceptions import RoleNotFound
from app.modules.role.infrastructure.persistence.role_document_mapper import (
    to_document,
    to_domain,
)
from bson import ObjectId
from pymongo.collection import Collection


class MongoRoleRepository(RoleRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, role: Role) -> Role:
        document = to_document(role)
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return to_domain(document)

    def get_by_id(self, role_id: str) -> Role | None:
        if not ObjectId.is_valid(role_id):
            return None

        document = self.collection.find_one({"_id": ObjectId(role_id)})
        return to_domain(document) if document else None

    def get_by_slug(self, slug: str) -> Role | None:
        document = self.collection.find_one({"slug": slug})
        return to_domain(document) if document else None

    def get_all(self) -> list[Role]:
        return [to_domain(document) for document in self.collection.find()]

    def update(self, role: Role) -> Role:
        if role.id is None or not ObjectId.is_valid(role.id):
            raise RoleNotFound("Role not found")

        result = self.collection.update_one(
            {"_id": ObjectId(role.id)},
            {"$set": to_document(role)},
        )
        if result.matched_count == 0:
            raise RoleNotFound("Role not found")

        updated = self.collection.find_one({"_id": ObjectId(role.id)})
        if updated is None:
            raise RoleNotFound("Role not found after update")
        return to_domain(updated)

    def delete(self, role_id: str) -> bool:
        if not ObjectId.is_valid(role_id):
            return False

        result = self.collection.delete_one({"_id": ObjectId(role_id)})
        return result.deleted_count > 0
