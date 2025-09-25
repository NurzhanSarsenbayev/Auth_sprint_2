from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr, Field
from schemas.role import RoleResponse


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=3)


class UserRead(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True  # нужно для SQLAlchemy моделей


class UserResponse(BaseModel):
    user_id: UUID = Field(alias="id")
    username: str
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True  # позволяет маппить ORM -> Pydantic
        populate_by_name = True


class CurrentUserResponse(BaseModel):
    user_id: Optional[UUID] = Field(alias="id", default=None)
    username: str
    email: Optional[EmailStr] = None
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True
        populate_by_name = True


# ----- auth/history -----
class LoginHistoryItem(BaseModel):
    user_id: UUID
    login_time: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    successful: bool

    class Config:
        from_attributes = True  # позволяет конвертировать напрямую из ORM


# ----- auth/update -----
class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    old_password: Optional[str] = Field(None, min_length=3, max_length=50)
    new_password: Optional[str] = Field(None, min_length=3)


class UserUpdateResponse(BaseModel):
    message: str
