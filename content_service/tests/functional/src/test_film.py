import pytest
import pytest_asyncio
from aiohttp import ClientSession
from http import HTTPStatus
from functional.settings import settings


@pytest.mark.asyncio
async def test_film_validation(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/films/123"
    ) as resp:
        # Assert
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_film_by_id(http_session: ClientSession,es_ready):
    # Arrange
    film_id = "900e93d9-21f2-4c62-b8d2-32de32110a16"

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/films/{film_id}"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert data["uuid"] == film_id


@pytest.mark.asyncio
async def test_get_all_films(http_session: ClientSession,es_ready):
    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/films/?page=1&size=10"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert isinstance(data, list)
    assert len(data) <= 10

    if data:
        assert "title" in data[0]
        assert "uuid" in data[0]


@pytest.mark.asyncio
async def test_film_cache(http_session: ClientSession, redis_client,es_ready):
    # Arrange
    film_id = "900e93d9-21f2-4c62-b8d2-32de32110a16"
    await redis_client.flushdb()

    # Act 1 (кэш пуст → идём в API)
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/films/{film_id}"
    ) as resp1:
        data1 = await resp1.json()

    # Assert 1
    assert resp1.status == HTTPStatus.OK
    keys = await redis_client.keys("*")
    assert len(keys) > 0

    # Act 2 (повторный запрос → идём в кэш)
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/films/{film_id}"
    ) as resp2:
        data2 = await resp2.json()

    # Assert 2
    assert resp2.status == HTTPStatus.OK
    assert data1 == data2
