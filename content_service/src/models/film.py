from uuid import UUID

from models.genre import Genre
from models.person import Person
from pydantic import BaseModel


class Film(BaseModel):
    """
    Полная информация о фильме, включая описание, рейтинг, жанры и участников.

    Attributes:
        uuid (UUID): Уникальный идентификатор фильма.
        title (str): Название фильма.
        description (Optional[str]): Краткое описание фильма.
        imdb_rating (Optional[float]): Рейтинг IMDb (может отсутствовать).
        genres (List[Genre]): Список жанров фильма.
        actors (List[Person]): Список актёров, участвовавших в фильме.
        writers (List[Person]): Список сценаристов.
        directors (List[Person]): Список режиссёров.
    """

    uuid: UUID
    title: str
    description: str | None = None
    imdb_rating: float | None = None
    genres: list[Genre] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
