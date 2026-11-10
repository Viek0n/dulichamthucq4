from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: str
    slug: str
    name: str
    permissions: list[str]
    priority: int
