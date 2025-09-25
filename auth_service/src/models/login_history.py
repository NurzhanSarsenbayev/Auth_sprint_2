import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.postgres import Base


class LoginHistory(Base):
    __tablename__ = "login_history"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True),
                     ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="login_history")
