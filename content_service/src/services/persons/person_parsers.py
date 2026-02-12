from typing import Any
from uuid import UUID

from models.film import Film
from models.film_short import FilmShort
from models.person import Person


def parse_persons_from_agg(response: dict) -> list[Person]:
    """
    Парсим агрегации actors/writers/directors
    в единый список персон без дублей.
    """
    persons_dict: dict[str, str] = {}

    for role in ("actors", "writers", "directors"):
        buckets = (
            response.get("aggregations", {}).get(role, {}).get("persons", {}).get("buckets", [])
        )
        for bucket in buckets:
            uuid = bucket["key"]
            name_buckets = bucket.get("name", {}).get("buckets", [])
            if name_buckets:
                full_name = name_buckets[0]["key"]
                persons_dict[uuid] = full_name

    # преобразуем в список Person
    return [Person(uuid=uid, full_name=name) for uid, name in persons_dict.items()]


def parse_persons_from_hits(hits: list[dict[str, Any]]) -> list[Person]:
    """Достаёт всех персон с
    привязкой к фильмам из документов ES."""
    persons_dict: dict[str, Person] = {}

    for doc in hits:
        source = doc.get("_source", {})
        film = Film(uuid=source["id"], title=source["title"], imdb_rating=source.get("imdb_rating"))

        for role in ["actors", "directors", "writers"]:
            for p in source.get(role, []):
                person_id = p["uuid"]
                if person_id not in persons_dict:
                    persons_dict[person_id] = Person(
                        uuid=person_id, full_name=p["full_name"], films=[]
                    )
                persons_dict[person_id].films.append(film)

    return list(persons_dict.values())


def parse_person_with_films(hits: list[dict[str, Any]], person_id: UUID) -> Person | None:
    """Возвращает персону по UUID + список фильмов, где она участвовала."""
    if not hits:
        return None

    films: list[FilmShort] = []
    person: Person | None = None

    for doc in hits:
        src = doc["_source"]

        # сохраняем фильм
        films.append(
            FilmShort(
                uuid=UUID(src["uuid"]), title=src["title"], imdb_rating=src.get("imdb_rating")
            )
        )

        # ищем персону в ролях
        for role in ["actors", "directors", "writers"]:
            for p in src.get(role, []):
                if p["uuid"] == str(person_id):
                    if not person:
                        person = Person(
                            uuid=UUID(p["uuid"]),
                            full_name=p["full_name"],
                            role=role[:-1],  # actor / director / writer
                            films=[],
                        )

    if person:
        person.films = films

    return person


def parse_persons_with_name(hits: list[dict[str, Any]], query_str: str) -> list[Person]:
    """Достаёт уникальных персон
     по имени из документов ES
    (регистронезависимый поиск)."""
    result = []
    seen = set()
    normalized_query = query_str.strip().lower()

    for doc in hits:
        src = doc["_source"]
        for role in ["actors", "directors", "writers"]:
            for p in src.get(role, []):
                if p["uuid"] not in seen and p["full_name"].strip().lower() == normalized_query:
                    seen.add(p["uuid"])
                    result.append(
                        Person(
                            uuid=UUID(p["uuid"]),
                            full_name=p["full_name"],
                            role=role[:-1],  # убираем "s"
                        )
                    )
    return result
