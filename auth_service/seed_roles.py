import argparse
import uuid
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models import Role


def seed(db_url: str | None = None):
    url = (db_url or settings.database_url).replace("+asyncpg", "")
    engine = create_engine(url, echo=False, future=True)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        for name, desc in [
            ("user", "Authenticated user"),
            ("subscriber", "Authenticated subscriber"),
            ("admin", "Administrator"),
            ("moderator", "Moderator"),
            ("guest", "Anonymous / guest"),
        ]:
            role = session.execute(
                select(Role).where(Role.name == name)).scalar_one_or_none()
            if not role:
                role = Role(
                    role_id=uuid.uuid4(),
                    name=name,
                    description=desc,
                    created_at=datetime.utcnow()
                )
                session.add(role)
        session.commit()
        print("✅ Roles seeded")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, help="Database URL")
    args = parser.parse_args()
    seed(args.db)
