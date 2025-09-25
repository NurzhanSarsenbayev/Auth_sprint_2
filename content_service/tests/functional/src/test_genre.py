import pytest
import pytest_asyncio
from aiohttp import ClientSession
from http import HTTPStatus
from functional.settings import settings


@pytest.mark.asyncio
async def test_genre_validation(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/genres/123"
    ) as resp:
        # Assert
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_genre_by_id(http_session: ClientSession, es_ready):
    # Arrange
    genre_id = "babf7031-6c46-4a02-aaf4-e3e17d948a82"

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/genres/{genre_id}"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert "uuid" in data
    assert "name" in data
    assert data["uuid"] == genre_id


@pytest.mark.asyncio
async def test_get_all_genres(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/genres/"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert isinstance(data, list)
    assert len(data) > 0

    genre = data[0]
    assert "uuid" in genre
    assert "name" in genre


@pytest.mark.asyncio
async def test_genre_cache(redis_client, http_session: ClientSession, es_ready):
    # Arrange
    genre_id = "babf7031-6c46-4a02-aaf4-e3e17d948a82"
    await redis_client.flushall()

    # Act 1 (кэш пуст → идём в API/ES)
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/genres/{genre_id}"
    ) as resp1:
        data1 = await resp1.json()

    # Assert 1
    assert resp1.status == HTTPStatus.OK
    assert data1["uuid"] == genre_id
    keys = await redis_client.keys("*")
    assert len(keys) > 0

    # Act 2 (кэш уже есть → возвращаем из Redis)
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/genres/{genre_id}"
    ) as resp2:
        data2 = await resp2.json()

    # Assert 2
    assert resp2.status == HTTPStatus.OK
    assert data1 == data2