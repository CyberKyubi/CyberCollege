import asyncio

from aiogram import Dispatcher
from aiogram.types import Message

from locales.ru import BotMessages, BotButtons
from states.owner_state_machine import DeployStates
from storages.redis.storage import RedisStorage


async def fill_redis(message: Message, redis__db_1: RedisStorage):
    users = {'users_data': {}, 'users_id': []}
    await redis__db_1.set_data('users', users)

    await message.answer(BotMessages.redis_is_ready)


def register_fill_redis(dp: Dispatcher):
    dp.register_message_handler(
        fill_redis,
        text=BotButtons.fill_redis,
        state=DeployStates.deploy
    )