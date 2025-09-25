import asyncio
import json
import logging

import redis.asyncio as redis
import pytest_asyncio
import aiohttp
from elasticsearch import AsyncElasticsearch, helpers

from functional.testdata.es_mapping import MOVIES_MAPPING
from functional.settings import settings


logger = logging.getLogger(__name__)

# ---------- aiohttp session ----------
@pytest_asyncio.fixture
async def http_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


# ---------- elasticsearch client ----------
@pytest_asyncio.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(hosts=[f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"])
    yield client
    await client.close()

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------- redis client ----------
@pytest_asyncio.fixture()
async def redis_client(event_loop):
    client = await redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        decode_responses=True
    )
    yield client
    await client.aclose()

# ---------- prepare elasticsearch with data ----------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_es(es_client):
    # пересоздаём индекс
    if await es_client.indices.exists(index=settings.ELASTIC_INDEX):
        await es_client.indices.delete(index=settings.ELASTIC_INDEX)

    await es_client.indices.create(index=settings.ELASTIC_INDEX, body=MOVIES_MAPPING)

    actions = []
    with open("functional/testdata/test_data.json", "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            doc = json.loads(line)

            # поддерживаем оба варианта: экспорт из ES и "простой" json
            doc_id = doc.get("_id") or doc.get("id") or doc.get("uuid")
            source = doc.get("_source") or doc

            if not doc_id:
                logger.error(f"Не найден ID в документе: {doc}")
                raise ValueError(f"❌ Не найден ID в документе: {doc}")

            actions.append({
                "_index": settings.ELASTIC_INDEX,
                "_id": doc_id,
                "_source": source,
            })

    # bulk insert + refresh=wait_for
    if actions:
        success, errors = await helpers.async_bulk(
            es_client,
            actions,
            raise_on_error=False,
            refresh="wait_for"
        )
        if errors:
            logger.warning(f"Ошибки при загрузке данных в ES: {errors}")

    # проверка загрузки
    count = await es_client.count(index=settings.ELASTIC_INDEX)
    assert count["count"] > 0, "❌ Данные не загрузились в Elasticsearch"
    logger.info(f"Загружено {count['count']} документов в ES")

@pytest_asyncio.fixture(scope="session")
async def es_ready(setup_es):
    # просто прокидываем флаг
    return setup_es