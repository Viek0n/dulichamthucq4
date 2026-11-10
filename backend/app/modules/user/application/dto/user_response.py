from pydantic import BaseModel

from app.modules.user.domain.entities.user import UserStatus


class UserResponse(BaseModel):
    id: str
    is_poi_owner_verified: bool
    status: UserStatus
    name: str
    email: str
    phone: str
    role_id: str


class UserTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
