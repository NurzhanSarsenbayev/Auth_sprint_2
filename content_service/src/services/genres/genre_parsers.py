from uuid import UUID
from typing import List, Optional, Dict, Any

from models.genre import Genre


def parse_genres_from_agg(resp: dict) -> List[Genre]:
    buckets = resp["aggregations"]["unique_genres"]["by_uuid"]["buckets"]
    genres = []

    for bucket in buckets:
        uuid = bucket["key"]
        hits = bucket["name"]["hits"]["hits"]
        if not hits:
            continue
        # Берём name прямо из nested top_hits
        name = hits[0]["_source"]["name"]
        genres.append(Genre(uuid=UUID(uuid), name=name))

    return genres


def parse_genre_from_hit(hits: List[Dict[str, Any]], genre_uuid: UUID) -> Optional[Genre]:
    """Ищет жанр по UUID в результатах ES."""
    if not hits:
        return None
    for g in hits[0]["_source"].get("genres", []):
        if g["uuid"] == str(genre_uuid):
            return Genre(uuid=UUID(g["uuid"]), name=g["name"])
    return None


def parse_genres_with_filter(hits: List[Dict[str, Any]], query_str: str) -> List[Genre]:
    """Фильтрует жанры по подстроке (поиск)."""
    unique = {}
    for doc in hits:
        for g in doc["_source"].get("genres", []):
            name = g.get("name")
            uuid_str = g.get("uuid")
            if name and uuid_str and query_str.lower() in name.lower():
                unique[uuid_str] = Genre(uuid=UUID(uuid_str), name=name)
    return list(unique.values())
