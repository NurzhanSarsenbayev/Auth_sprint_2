from uuid import UUID


def all_genres_query(size: int = 1000) -> dict:
    return {
        "size": 0,  # не нужны документы
        "aggs": {
            "unique_genres": {
                "nested": {"path": "genres"},
                "aggs": {
                    "by_uuid": {
                        "terms": {"field": "genres.uuid", "size": size},
                        "aggs": {
                            "name": {
                                "top_hits": {
                                    "_source": ["genres.name"],
                                    "size": 1
                                }
                            }
                        }
                    }
                }
            }
        }
    }

def genre_by_id_query(genre_id: UUID) -> dict:
    return {
        "size": 1,
        "query": {
            "nested": {
                "path": "genres",
                "query": {"term": {"genres.uuid": str(genre_id)}},
            }
        },
        "_source": ["genres"],
    }


def search_genres_query(query_str: str) -> dict:
    return {
        "_source": ["genres"],
        "query": {
            "nested": {
                "path": "genres",
                "query": {
                    "match": {
                        "genres.name": {
                            "query": query_str,
                            "operator": "and",
                        }
                    }
                },
                "inner_hits": {},
            }
        },
    }
