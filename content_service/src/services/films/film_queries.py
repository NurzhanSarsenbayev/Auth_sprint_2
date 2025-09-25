from uuid import UUID


def all_films_query(page: int, size: int, sort: str) -> dict:
    sort_field = sort.lstrip("-")
    sort_order = "desc" if sort.startswith("-") else "asc"

    return {
        "from": (page - 1) * size,
        "size": size,
        "sort": [{sort_field: {"order": sort_order}}],
        "_source": ["uuid", "title", "imdb_rating"],
    }


def film_by_id_query(film_id: UUID) -> dict:
    return {
        "query": {"term": {"uuid": str(film_id)}},
        "size": 1,
    }

def search_films_query(query_str: str,page: int, size: int) -> dict:
    return {
        "from": (page - 1) * size,
        "size": size,
        "_source": ["uuid", "title", "imdb_rating"],
        "query": {
            "multi_match": {
                "query": query_str,
                "fields": ["title^2", "title.raw^5"],  # буст для точного совпадения
                "operator": "AND",
                "fuzziness": "1",
            }
        },
    }