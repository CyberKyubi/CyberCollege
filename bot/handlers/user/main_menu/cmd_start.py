from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from states.user_state_machine import RegistrationStates
from storages.redis.storage import RedisStorage
from storages.db.requests import select__all_users
from handlers.user.main_menu.menu import user__main_menu


async def user__cmd_start(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    users = await redis__db_1.get_data('users')
    if not users.get('users_id'):
        result = await select__all_users(session_pool)
        users_data, users_id = {}, []
        if result:
            for user_id, college_group, college_building in result:
                users_data[str(user_id)] = {
                    'current_group': {'college_building': college_building, 'group': college_group},
                    'default_college_group': college_group, 'default_college_building': college_building,
                    'groups_friends': [], 'group_added': ''
                }
            users_id = list(users_data.keys())
            await redis__db_1.set_data('users', dict(users_data=users_data, users_id=users_id))
    else:
        users_data = users['users_data']
        users_id = users['users_id']

    # Зарегистрирован ли студент #
    user_id = str(message.from_user.id)
    if user_id not in users_id:
        await message.answer(BotMessages.college_group__input, reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.college_group__input)
        return

    college_group = users_data[user_id]['current_group']['group']
    await user__main_menu(message, state, college_group)


def register_user__cmd_start(dp: Dispatcher):
    dp.register_message_handler(
        user__cmd_start,
        CommandStart(),
        state='*'
    )
