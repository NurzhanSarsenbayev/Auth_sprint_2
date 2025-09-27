import os
import sys
sys.path.append("src")
from logging.config import fileConfig
from db.postgres import Base
from sqlalchemy import create_engine, pool
from alembic import context
from core.config import settings
from models.user import User
from models.role import Role
from models.user_role import UserRole
from models.login_history import LoginHistory
from models.social_account import SocialAccount



config = context.config
fileConfig(config.config_file_name)

# url берём либо из alembic.ini, либо из env
url = (
    config.get_main_option("sqlalchemy.url")
    or os.getenv("DB_URL")
    or settings.database_url
)

# ✅ если async URL → заменяем на sync
url = url.replace("+asyncpg", "")

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
