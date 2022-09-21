import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit=1, key_prefix='antiflood_'):
        super().__init__()
        self.rate_limit = rate_limit
        self.prefix = key_prefix

    async def on_process_message(self, message: Message, data: dict):
        handler = current_handler.get()
        dp = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f'{self.prefix}_{handler.__name__}')
        else:
            limit = self.rate_limit
            key = f'{self.prefix}_message'
        try:
            await dp.throttle(key, rate=limit)
        except Throttled:
            logging.info(f'Throttled: пользователь={message.from_user.id} | info=')
            raise CancelHandler()