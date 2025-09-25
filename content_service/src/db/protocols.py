from typing import Protocol, Any, Optional


class CacheStorageProtocol(Protocol):
    """Протокол для кэша (Redis)."""

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение по ключу.
        Возвращает None, если ключа нет.
        """
        ...

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """Сохранить значение по ключу с возможным временем жизни (expire в секундах)."""
        ...


class SearchStorageProtocol(Protocol):
    """Протокол для поискового хранилища (Elasticsearch)."""

    async def get(self, index: str, id: str) -> Optional[dict]:
        """Получить документ по id."""
        ...

    async def search(
        self,
        index: str,
        query: dict,
        size: int = 10,
        from_: int = 0,
    ) -> list[dict]:
        """Выполнить поиск по индексу и запросу."""
        ...