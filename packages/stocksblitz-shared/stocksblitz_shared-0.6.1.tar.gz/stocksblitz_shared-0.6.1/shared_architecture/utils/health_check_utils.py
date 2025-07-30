import logging

from shared_architecture.connections.redis_client import get_redis_client
from shared_architecture.connections.timescaledb_client import get_timescaledb_session

async def check_redis():
    try:
        redis = await get_redis_client()
        pong = await redis.ping()
        return True, f"Redis ping response: {pong}"
    except Exception as e:
        logging.exception("Redis health check failed.")
        return False, str(e)


async def check_timescaledb():
    try:
        session = get_timescaledb_session()
        await session.execute("SELECT 1;")
        await session.close()
        return True, "TimescaleDB connection successful"
    except Exception as e:
        logging.exception("TimescaleDB health check failed.")
        return False, str(e)

async def health_check_all():
    checks = {
        "redis": await check_redis(),
        "timescaledb": await check_timescaledb()
    }
    return checks
