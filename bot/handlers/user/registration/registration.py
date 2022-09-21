import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotErrors
from states.user_state_machine import RegistrationStates
from storages.redis.storage import RedisStorage
from storages.db.requests import select__all_college_groups, insert__new_user
from handlers.user.main_menu.menu import user__main_menu


async def college_group__input(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    """
    Получает введенную группу, если такая есть, то добавляем нового cтудента.
    :param message:
    :param state:
    :param session_pool:
    :param redis__db_1:
    :return:
    """
    users, college_groups = await redis__db_1.get_multiple_data('users', 'college_groups')
    users_data = users.get('users_data')

    if not college_groups:
        college_groups = await select__all_college_groups(session_pool)
        await redis__db_1.set_data('college_groups', college_groups)

    user_id = str(message.from_user.id)
    college_group = message.text

    if college_group in college_groups['Туполева,17а']:
        college_building = 'Туполева,17а'
    elif college_group in college_groups['Курчатова,16']:
        college_building = 'Курчатова,16'
    else:
        await message.answer(BotErrors.college_group_not_found)
        return

    users_data[user_id] = {
        'current_group': {'college_building': college_building, 'group': college_group},
        'default_college_group': college_group, 'default_college_building': college_building,
        'groups_friends': [], 'group_added': ''
    }
    users['users_id'].append(user_id)
    await redis__db_1.set_data('users', users)
    await insert__new_user(session_pool, message.from_user.id, college_group, college_building)
    logging.info(f'Новый студент | user_id [{user_id}] college_group [{college_group}] |')

    await user__main_menu(message, state, college_group)


def register_college_group__input(dp: Dispatcher):
    dp.register_message_handler(
        college_group__input,
        content_types=['text'],
        state=RegistrationStates.college_group__input
    )