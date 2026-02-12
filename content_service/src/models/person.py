from uuid import UUID

from models.film_short import FilmShort
from pydantic import BaseModel


class Person(BaseModel):
    """
    Модель персоны (актёра, режиссёра или сценариста).

    Attributes:
        uuid (UUID): Уникальный идентификатор персоны.
        full_name (str): Полное имя персоны.
        role (Optional[str]): Роль персоны
        (например, "actor", "director", "writer"). Может быть None.
        films (list[FilmShort]): Список фильмов где они учавствовали.
    """

    uuid: UUID
    full_name: str
    role: str | None = None
    films: list[FilmShort] = []
