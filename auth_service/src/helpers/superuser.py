# helpers/superuser.py
import uuid
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import User, Role, UserRole
from utils.security import hash_password


def ensure_superuser(db_url: str):
    """Создаёт суперпользователя и роль admin, если их нет"""
    engine = create_engine(db_url, echo=False, future=True)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        user = session.execute(
            select(User).where(User.email == "admin@example.com")
        ).scalar_one_or_none()

        if not user:
            user = User(
                user_id=uuid.uuid4(),
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("123"),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(user)
            session.flush()

        role = session.execute(
            select(Role).where(Role.name == "admin")
        ).scalar_one_or_none()

        if not role:
            role = Role(
                role_id=uuid.uuid4(),
                name="admin",
                description="Administrator role",
                created_at=datetime.utcnow(),
            )
            session.add(role)
            session.flush()

        user_role = session.execute(
            select(UserRole).where(
                UserRole.user_id == user.user_id,
                UserRole.role_id == role.role_id,
            )
        ).scalar_one_or_none()

        if not user_role:
            user_role = UserRole(
                id=uuid.uuid4(),
                user_id=user.user_id,
                role_id=role.role_id,
                assigned_at=datetime.utcnow(),
            )
            session.add(user_role)

        session.commit()
        print("✅ Superuser ensured")
