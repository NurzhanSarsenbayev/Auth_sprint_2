import pytest
import pytest_asyncio
from aiohttp import ClientSession
from http import HTTPStatus
from functional.settings import settings


@pytest.mark.asyncio
async def test_search_validation(http_session: ClientSession):
    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/search/?size=-1&query=test"
    ) as resp1:
        # Assert
        assert resp1.status == HTTPStatus.UNPROCESSABLE_ENTITY

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/search/?query="
    ) as resp2:
        # Assert
        assert resp2.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_search_limit_records(http_session: ClientSession, es_ready):
    # Arrange
    N = 2

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/search/?query=test&size={N}"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert len(data["films"]) <= N
    assert len(data["persons"]) <= N
    assert len(data["genres"]) <= N


@pytest.mark.asyncio
async def test_search_by_phrase(http_session: ClientSession, es_ready):
    # Arrange
    phrase = "Star Wars"

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/search/?query={phrase}&page=1&size=5"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert (
        any(phrase.lower() in f["title"].lower() for f in data["films"])
        or any(phrase.lower() in p["full_name"].lower() for p in data["persons"])
        or any(phrase.lower() in g["name"].lower() for g in data["genres"])
    )


@pytest.mark.asyncio
async def test_search_cache(http_session: ClientSession, redis_client, es_ready):
    # Arrange
    phrase = "Star Wars"
    await redis_client.flushdb()

    # Act 1
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/search/?query={phrase}&page=1&size=3"
    ) as resp1:
        data1 = await resp1.json()

    # Assert 1
    assert resp1.status == HTTPStatus.OK

    # Act 2
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/search/?query={phrase}&page=1&size=3"
    ) as resp2:
        data2 = await resp2.json()

    # Assert 2
    assert resp2.status == HTTPStatus.OK
    assert data1 == data2
