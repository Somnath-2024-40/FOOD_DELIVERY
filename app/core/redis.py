import redis.asyncio as r

from  core.config import settings

redis_client : r.Redis = None

async def get_redis()-> r.Redis:
    return redis_client


async def init_redis():
    global redis_client
    redis_client = r.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis():
    if redis_client:
        await redis_client.close()



