from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: str
    name: str
    permissions: list[str]
    priority: int
