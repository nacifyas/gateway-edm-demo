from config.redis_conf import redis, redis_stream
import pytest


@pytest.mark.asyncio
async def test_db_connection():
    assert await redis.ping() == True


@pytest.mark.asyncio
async def test_stream_connection():
    assert await redis_stream.ping() == True
