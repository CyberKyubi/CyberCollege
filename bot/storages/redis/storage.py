import logging
from typing import Dict, Union, Tuple

import orjson as json
import aioredis


class RedisStorage:
    """
    Класс для работы с хранилищем redis.
    """
    def __init__(self, redis: aioredis.client.Redis):
        self._redis_conn = redis
        self.user = 'bot'

    @staticmethod
    def generate_key(*parts):
        """
        Генерирует ключ для throttling.
        :param parts:
        :return:
        """
        return ''.join(tuple(map(str, parts)))

    async def set_throttle_key(self, user_id: str):
        """
        Устанавливает на студента на час throttle ключ.
        :param user_id:
        :return:
        """
        async with self._redis_conn as redis:
            key = self.generate_key(user_id, 'throttling')
            logging.info(f'Redis instance [{redis}] | key [{key}] | Запись данных.')
            await redis.setex(key, 3600, json.dumps('throttled'))
        logging.info(f'Студент [{user_id} throttled]')

    async def get_throttle_key(self, user_id: str):
        """
        Забирает данные throttled студнета.
        :param user_id:
        :return:
        """
        redis = self._redis_conn
        key = self.generate_key(user_id, 'throttling')
        logging.info(f'Redis instance [{redis}] | key [{key}] | Получение данных.')
        result = await redis.get(key)
        data = json.loads(result) if result else {}
        return data

    async def set_data(self, key: str, value: Union[dict, list, int, str]):
        """
        Записывает данные по ключу.
        :param key:
        :param value:
        :return:
        """
        async with self._redis_conn as redis:
            logging.info(f'Redis instance [{redis}] | key [{key}] | Запись данных.')
            redis_value = await redis.get(self.user)
            data = json.loads(redis_value) if redis_value else {}
            data[key] = value
            await redis.set(self.user, json.dumps(data))

    async def get_data(self, key: str) -> Dict:
        """
        Возвращает данные по ключу.
        :param key:
        :return:
        """
        redis = self._redis_conn
        logging.info(f'Redis instance [{redis}] | key [{key}] | Получение данных.')
        result = await redis.get(self.user)
        if result:
            json_data = json.loads(result)
            data = json_data.get(key, {})
            return data
        return {}

    async def get_multiple_data(self, key_1: str, key_2: str) -> Union[dict | Tuple[dict, dict]]:
        """
        Забирает данные по двум ключам.
        :param key_1:
        :param key_2:
        :return:
        """
        redis = self._redis_conn
        logging.info(f'Redis instance [{redis}] | key_1 [{key_1}] key_2 [{key_2}] | Получение данных по двум ключам')
        result = await redis.get(self.user)
        if result:
            json_data = json.loads(result)
            data = json_data.get(key_1, {})
            data_2 = json_data.get(key_2, {})
            return data, data_2
        return {}

    async def delete_all_data(self):
        """
        Удаляет все данные.
        :return:
        """
        async with self._redis_conn as redis:
            logging.info(f'Redis instance [{redis}] | Удаление всех данных.')
            result = await redis.get(self.user)
            if result:
                await redis.delete(self.user)

    async def delete_key(self, key: str):
        """
        Удаляет указанный ключ.
        :param key:
        :return:
        """
        async with self._redis_conn as redis:
            logging.info(f'Redis instance [{redis}] | key [{key}] | Удаление данных.')
            result = await redis.get(self.user)
            if result:
                data = json.loads(result)
                if data.get(key):
                    data.pop(key)
                    await redis.set(self.user, json.dumps(data))

    async def delete_user(self, user_id: str):
        """
        Удаляет студента.
        :param user_id:
        :return:
        """
        async with self._redis_conn as redis:
            logging.info(f'Redis instance [{redis}] | user_id [{user_id}] | Удаление студента.')
            result = await redis.get(self.user)
            data = json.loads(result)
            users = data.get('users')

            users['users_data'].pop(user_id)
            users['users_id'].remove(user_id)
            data['users'] = users
            await redis.set(self.user, json.dumps(data))