import argparse
import uuid
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models import User, Role, UserRole
from utils.security import hash_password
import os


def create_superuser(db_url: str | None = None):
    # 1. если явно передали --db → берём его
    if db_url:
        url = db_url

    # 2. если переменная окружения TESTING=1 → берём test_settings
    elif os.getenv("TESTING", "0") == "1":
        from core.test_config import test_settings  # <-- ВНУТРИ
        url = test_settings.database_url

    # 3. иначе → обычные settings
    else:
        url = settings.database_url

    # SQLAlchemy sync-движок (без asyncpg)
    url = url.replace("+asyncpg", "")

    print(f"Using database URL: {url}")

    engine = create_engine(url, echo=False, future=True)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # проверяем, есть ли админ
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

        # проверяем, есть ли роль admin
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

        # проверяем связку user-role
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
        print("Superuser created or already exists ✅")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create superuser in database")
    parser.add_argument("--db", type=str, help="Database URL (optional)")
    args = parser.parse_args()

    create_superuser(args.db)
