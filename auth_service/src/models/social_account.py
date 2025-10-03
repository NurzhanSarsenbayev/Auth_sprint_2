import uuid
from sqlalchemy import (Column,
                        String,
                        ForeignKey,
                        DateTime,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.postgres import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),
                     ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False)

    provider = Column(String(50), nullable=False)  # "yandex", "google", "vk"
    provider_account_id = Column(String(255),
                                 nullable=False)  # уникальный id у провайдера

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id",
                         name="uq_provider_account"),
    )

    # ORM-связь: user.social_accounts
    user = relationship("User", back_populates="social_accounts")
