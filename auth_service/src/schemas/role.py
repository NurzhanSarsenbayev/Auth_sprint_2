from pydantic import BaseModel, ConfigDict, model_validator
from uuid import UUID
from typing import Optional
from datetime import datetime


class RoleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: UUID
    name: str
    description: str | None


class RoleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    description: Optional[str] = None


# assign / remove / check
class RoleAssignRequest(BaseModel):
    user_id: UUID
    role_id: Optional[UUID] = None

    @model_validator(mode="after")
    def check_role(self):
        if not self.role_id and not self.role_name:
            raise ValueError("Either role_id or role_name must be provided")
        return self


class RoleCheckRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    role_name: str


class RoleCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    allowed: bool
