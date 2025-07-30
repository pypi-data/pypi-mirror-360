# -*- coding:utf-8 -*-
"""
@Time : 2022/4/25 2:09 PM
@Author: binkuolo
@Des: redis
"""

import redis
from descartcan.config import config


async def get_redis_client() -> redis.asyncio.Redis | None:
    if config.REDIS_HOST and config.REDIS_PORT:
        sys_cache_pool = redis.asyncio.ConnectionPool.from_url(
            f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}",
            db=config.REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
        )
        return redis.asyncio.Redis(connection_pool=sys_cache_pool)
    return None
