import logging
from typing import Optional

import aioredis


class RedisPool:
    def __init__(self, redis_uri: str = None):
        self._redis_uri = redis_uri

        self._redis_pool: Optional[aioredis.ConnectionPool] = None

    async def connect(self):
        self._redis_pool = aioredis.from_url(self._redis_uri)
        logging.warning(f"Created redis pool: {self._redis_pool}")
        return self._redis_pool
