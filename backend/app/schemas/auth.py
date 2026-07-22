from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info) -> str:
        return str(id)

    model_config = {"from_attributes": True}
