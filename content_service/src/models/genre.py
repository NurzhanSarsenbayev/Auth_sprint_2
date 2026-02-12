from uuid import UUID

from pydantic import BaseModel


class Genre(BaseModel):
    """
    Модель жанра фильма.

    Attributes:
        uuid (UUID): Уникальный идентификатор жанра.
        name (str): Название жанра.
    """

    uuid: UUID
    name: str
