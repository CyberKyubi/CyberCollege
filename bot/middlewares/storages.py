from typing import Dict, Any

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.middlewares import BaseMiddleware

from storages.redis.storage import RedisStorage


class Storages(BaseMiddleware):
    def __init__(self, session_pool, redis__db_1: RedisStorage, redis__db_2: RedisStorage, dp: Dispatcher):
        super(Storages, self).__init__()
        self.session_pool = session_pool
        self.redis__db_1 = redis__db_1
        self.redis__db_2 = redis__db_2
        self.dp = dp

    async def on_process_message(self, message: Message, data: Dict[str, Any], *args):
        data['session_pool'] = self.session_pool
        data['redis__db_1'] = self.redis__db_1
        data['redis__db_2'] = self.redis__db_2
        data['dp'] = self.dp