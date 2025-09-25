from core.config import settings
from core.test_config import test_settings

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import Request

Base = declarative_base()


def make_engine(db_url: str | None = None, echo: bool = False):
    """Создаёт async-движок под указанную базу."""
    dsn = db_url or (
        test_settings.database_url if settings.testing
        else settings.database_url)
    return create_async_engine(dsn, echo=echo, future=True)


def make_session_factory(engine):
    """Создаёт фабрику async-сессий."""
    return sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session(request: Request) -> AsyncSession:
    """
    FastAPI-dependency: отдаёт AsyncSession.
    Делает rollback при исключениях и гарантирует закрытие сессии.
    """
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            # async with сам закроет соединение, но явный close читабельнее и
            # удовлетворяет требованию ревьюера
            await session.close()
