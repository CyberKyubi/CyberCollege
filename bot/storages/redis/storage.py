from typing import Dict, Union, Optional

import orjson as json
import aioredis


class RedisStorage:
    def __init__(self, redis: aioredis.client.Redis):
        self._redis_conn = redis
        self.user = 'bot'

    async def set_data(self, key: str, value: Union[dict, list, int, str]):
        async with self._redis_conn as redis:
            redis_value = await redis.get(self.user)
            data = json.loads(redis_value) if redis_value else {}
            data[key] = value
            await redis.set(self.user, json.dumps(data))
            return data

    async def get_data(self, key: str) -> Dict:
        redis = self._redis_conn
        result = await redis.get(self.user)
        if result:
            json_data = json.loads(result)
            data = json_data.get(key, {})
            return data
        return {}

    async def delete_all_data(self, user_id: str):
        async with self._redis_conn as redis:
            result = await redis.get(user_id)
            if result:
                await redis.delete(user_id)

    async def delete_key(self, key: str):
        async with self._redis_conn as redis:
            result = await redis.get(self.user)
            if result:
                data = json.loads(result)
                if data.get(key):
                    data.pop(key)
                    await redis.set(self.user, json.dumps(data))

