from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from keyboards.reply_keyboard_markup import reply_markup
from states.state_machine import UserStates
from storages.redis.storage import RedisStorage
from storages.db.requests import select__all_users
from handlers.user.menu import users__menu


async def cmd_start(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    users = await redis__db_1.get_data('users')
    if not users:
        result = await select__all_users(session_pool)
        users_data = {str(user_id): {'college_group': college_group} for user_id, college_group in result}
        users = list(users_data.keys())
        await redis__db_1.set_data('users', dict(users_data=users_data, users_id=users))
    else:
        users = users['users_id']

    if str(message.from_user.id) not in users:
        await message.answer(BotMessages.select_college_group, reply_markup=reply_markup('groups'))
        await state.set_state(UserStates.select_college_group)
        return

    await users__menu(message, state)


def register_cmd_start(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start,
        CommandStart(),
        state='*'
    )
