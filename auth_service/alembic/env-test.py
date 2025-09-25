import sys
# from src import models  # важно: импортируем модели,
# чтобы они зарегистрировались в Base.metadata
from core.config import settings
from db.postgres import Base
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# добавляем src в sys.path, чтобы Alembic видел модели
sys.path.append("src")

# логирование Alembic
config = context.config
fileConfig(config.config_file_name)

# сюда попадут все таблицы из моделей
target_metadata = Base.metadata

# получаем URL БД: берём из alembic.ini / alembic_test.ini
db_url = config.get_main_option("sqlalchemy.url") or settings.database_url


def run_migrations_offline() -> None:
    """Запуск миграций в оффлайн-режиме (генерация SQL без подключения)."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме (через sync SQLAlchemy engine)."""
    connectable = engine_from_config(
        {"sqlalchemy.url": db_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
