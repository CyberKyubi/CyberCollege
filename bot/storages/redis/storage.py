from typing import Dict, Union, Tuple

import orjson as json
import aioredis


class RedisStorage:
    def __init__(self, redis: aioredis.client.Redis):
        self._redis_conn = redis
        self.user = 'bot'

    @staticmethod
    def generate_key(*parts):
        return ''.join(tuple(map(str, parts)))

    async def set_throttle_key(self, user_id: str):
        async with self._redis_conn as redis:
            key = self.generate_key(user_id, 'throttling')
            await redis.setex(key, 3600, json.dumps('throttled'))

    async def get_throttle_key(self, user_id: str):
        redis = self._redis_conn
        key = self.generate_key(user_id, 'throttling')
        result = await redis.get(key)
        data = json.loads(result) if result else {}
        return data

    async def set_data(self, key: str, value: Union[dict, list, int, str]):
        async with self._redis_conn as redis:
            redis_value = await redis.get(self.user)
            data = json.loads(redis_value) if redis_value else {}
            data[key] = value
            await redis.set(self.user, json.dumps(data))

    async def get_data(self, key: str) -> Dict:
        redis = self._redis_conn
        result = await redis.get(self.user)
        if result:
            json_data = json.loads(result)
            data = json_data.get(key, {})
            return data
        return {}

    async def get_multiple_data(self, key_1: str, key_2: str) -> Union[dict | Tuple[dict, dict]]:
        redis = self._redis_conn
        result = await redis.get(self.user)
        if result:
            json_data = json.loads(result)
            data = json_data.get(key_1, {})
            data_2 = json_data.get(key_2, {})
            return data, data_2
        return {}

    async def delete_all_data(self):
        async with self._redis_conn as redis:
            result = await redis.get(self.user)
            if result:
                await redis.delete(self.user)

    async def delete_key(self, key: str):
        async with self._redis_conn as redis:
            result = await redis.get(self.user)
            if result:
                data = json.loads(result)
                if data.get(key):
                    data.pop(key)
                    await redis.set(self.user, json.dumps(data))

