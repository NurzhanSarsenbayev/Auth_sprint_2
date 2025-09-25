from typing import Optional
from uuid import UUID

from models.film import Film
from models.film_short import FilmShort
from models.genre import Genre
from models.person import Person

def parse_film(doc: dict) -> Optional[Film]:
    """Парсинг полной информации о фильме из ES-документа."""
    if not doc or "_source" not in doc:
        return None

    src = doc["_source"]
    return Film(
        uuid=UUID(src["uuid"]),
        title=src.get("title"),
        description=src.get("description"),
        imdb_rating=src.get("imdb_rating"),
        genres=[Genre(uuid=UUID(g["uuid"]), name=g["name"]) for g in src.get("genres", [])],
        actors=[
            Person(uuid=UUID(a["uuid"]), full_name=a["full_name"], role="actor")
            for a in src.get("actors", [])
        ],
        writers=[
            Person(uuid=UUID(w["uuid"]), full_name=w["full_name"], role="writer")
            for w in src.get("writers", [])
        ],
        directors=[
            Person(uuid=UUID(d["uuid"]), full_name=d["full_name"], role="director")
            for d in src.get("directors", [])
        ],
    )


def parse_film_short(doc: dict) -> FilmShort:
    """Парсинг краткой информации о фильме из ES-документа."""
    src = doc["_source"]
    return FilmShort(
        uuid=UUID(src["uuid"]),
        title=src["title"],
        imdb_rating=src.get("imdb_rating"),
    )
