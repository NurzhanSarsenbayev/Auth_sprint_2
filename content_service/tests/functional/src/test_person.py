import pytest
import pytest_asyncio
from aiohttp import ClientSession
from http import HTTPStatus
from functional.settings import settings


@pytest.mark.asyncio
async def test_person_validation(http_session: ClientSession):
    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/persons/123"
    ) as resp:
        # Assert
        assert resp.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_person_by_id(http_session: ClientSession):
    # Arrange
    person_id = "15af8ae2-1b30-41f1-9573-824d12dd70cb"

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/persons/{person_id}"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert "uuid" in data
    assert data["uuid"] == person_id
    assert "full_name" in data
    assert isinstance(data["full_name"], str)


@pytest.mark.asyncio
async def test_get_all_persons(http_session: ClientSession, es_ready):
    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/persons/?page=1&size=5"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert isinstance(data, list)
    assert all("uuid" in p and "full_name" in p for p in data)


@pytest.mark.asyncio
async def test_person_films(http_session: ClientSession, es_ready):
    # Arrange
    person_id = "15af8ae2-1b30-41f1-9573-824d12dd70cb"

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/persons/{person_id}"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert isinstance(data, dict)
    assert "uuid" in data
    assert "full_name" in data
    assert "role" in data
    assert "films" in data

    assert isinstance(data["films"], list)
    for film in data["films"]:
        assert isinstance(film, dict)
        assert "uuid" in film and isinstance(film["uuid"], str)
        assert "title" in film and isinstance(film["title"], str)
        assert "imdb_rating" in film
        assert isinstance(film["imdb_rating"], (float, int)) or film["imdb_rating"] is None


# -------------------- Поиск с учётом кэша в Redis --------------------
@pytest.mark.asyncio
async def test_person_cache(http_session: ClientSession, redis_client, es_ready):
    # Arrange
    person_name = "George Lucas"
    await redis_client.flushdb()

    # Act 1
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/persons/?query={person_name}&page=1&size=3"
    ) as resp1:
        data1 = await resp1.json()

    # Assert 1
    assert resp1.status == HTTPStatus.OK

    # Act 2
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/persons/?query={person_name}&page=1&size=3"
    ) as resp2:
        data2 = await resp2.json()

    # Assert 2
    assert resp2.status == HTTPStatus.OK
    assert data1 == data2
