from typing import Any

from dependencies import get_search_service
from fastapi import APIRouter, Depends, Query
from models.search import SearchResults
from services.global_search.search_service import SearchService

router = APIRouter()


@router.get(
    "/", summary="Глобальный поиск по фильмам, персонам и жанрам", response_model=SearchResults
)
async def search_all(
    query: str = Query(..., min_length=1, description="Поисковая строка"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
) -> dict[str, Any]:
    return await search_service.search_all(query=query, page=page, size=size)
