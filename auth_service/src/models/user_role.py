import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.postgres import Base


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True),
                     ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False)
    role_id = Column(UUID(as_uuid=True),
                     ForeignKey("roles.role_id", ondelete="CASCADE"),
                     nullable=False)

    # когда назначили роль
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # связи
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
