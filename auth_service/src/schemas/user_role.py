from typing import List
from uuid import UUID

from pydantic import BaseModel, Field
from schemas.role import RoleResponse


# ----- список пользователей с ролями (только админ) -----
class UserRoleListResponse(BaseModel):
    user_id: UUID = Field(alias="id")
    username: str
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True  # позволяет маппить ORM -> Pydantic
        populate_by_name = True
