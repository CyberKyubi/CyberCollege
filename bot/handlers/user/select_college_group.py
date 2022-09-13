from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from states.state_machine import UserStates
from storages.redis.storage import RedisStorage
from storages.db.requests import insert__new_user
from .menu import users__menu


async def select_college_group__button(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    users = await redis__db_1.get_data('users')
    users_data = users['users_data']

    user_id = str(message.from_user.id)
    college_group = message.text

    users_data[user_id] = dict(college_group=college_group)
    users['users_id'].append(user_id)

    await redis__db_1.set_data('users', users)
    await insert__new_user(session_pool, tg_user_id=message.from_user.id, college_group=college_group)
    await users__menu(message, state)


def register_select_college_group(dp: Dispatcher):
    dp.register_message_handler(
        select_college_group__button,
        text=[BotButtons.group_1, BotButtons.group_2],
        state=UserStates.select_college_group
    )