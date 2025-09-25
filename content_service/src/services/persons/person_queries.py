from uuid import UUID


def all_persons_query(size: int = 100) -> dict:
    query = {
        "size": 0,
        "aggs": {
            "actors": {
                "nested": {"path": "actors"},
                "aggs": {
                    "persons": {
                        "terms": {"field": "actors.uuid", "size": size},
                        "aggs": {
                            "name": {"terms": {"field": "actors.full_name.raw", "size": 1}}
                        }
                    }
                },
            },
            "writers": {
                "nested": {"path": "writers"},
                "aggs": {
                    "persons": {
                        "terms": {"field": "writers.uuid", "size": size},
                        "aggs": {
                            "name": {"terms": {"field": "writers.full_name.raw", "size": 1}}
                        }
                    }
                },
            },
            "directors": {
                "nested": {"path": "directors"},
                "aggs": {
                    "persons": {
                        "terms": {"field": "directors.uuid", "size": size},
                        "aggs": {
                            "name": {"terms": {"field": "directors.full_name.raw", "size": 1}}
                        }
                    }
                },
            },
        },
    }
    return query

def person_by_id_query(person_id: UUID) -> dict:
    """Запрос для поиска персоны по UUID."""
    return {
        "query": {
            "bool": {
                "should": [
                    {"nested": {"path": "actors", "query": {"term": {"actors.uuid": str(person_id)}}}},
                    {"nested": {"path": "directors", "query": {"term": {"directors.uuid": str(person_id)}}}},
                    {"nested": {"path": "writers", "query": {"term": {"writers.uuid": str(person_id)}}}}
                ]
            }
        },
        "_source": ["uuid", "id", "title", "imdb_rating", "actors", "directors", "writers"],
        "size": 1000,
    }

def search_person_query(query_str: str) -> dict:
    """Запрос для поиска персоны по имени (во всех ролях)."""
    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "actors",
                            "query": {
                                "match": {
                                    "actors.full_name": {
                                        "query": query_str,
                                        "fuzziness": "auto"
                                    }
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "writers",
                            "query": {
                                "match": {
                                    "writers.full_name": {
                                        "query": query_str,
                                        "fuzziness": "auto"
                                    }
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "directors",
                            "query": {
                                "match": {
                                    "directors.full_name": {
                                        "query": query_str,
                                        "fuzziness": "auto"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        },
        "_source": [
            "actors.uuid", "actors.full_name",
            "writers.uuid", "writers.full_name",
            "directors.uuid", "directors.full_name"
        ],
        "size": 100
    }


def films_by_person_query(person_id: UUID, size: int = 50) -> dict:
    """Запрос для поиска фильмов, где участвовала персона."""
    return {
        "_source": ["uuid", "title", "imdb_rating"],
        "query": {
            "bool": {
                "should": [
                    {"nested": {"path": "actors", "query": {"term": {"actors.uuid": str(person_id)}}}},
                    {"nested": {"path": "writers", "query": {"term": {"writers.uuid": str(person_id)}}}},
                    {"nested": {"path": "directors", "query": {"term": {"directors.uuid": str(person_id)}}}},
                ],
                "minimum_should_match": 1
            }
        },
        "size": size,
        "track_total_hits": True
    }


