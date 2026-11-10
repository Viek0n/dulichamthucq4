from app.modules.role.domain.entities.role import Role


def to_domain(document: dict) -> Role:
    return Role(
        id=str(document["_id"]),
        name=document["name"],
        permissions=list(document["permissions"]),
        priority=document["priority"],
    )


def to_document(role: Role) -> dict:
    return {
        "name": role.name,
        "permissions": role.permissions,
        "priority": role.priority,
    }
