import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotErrors
from states.user_state_machine import RegistrationStates
from storages.redis.storage import RedisStorage
from storages.db.requests import insert__new_user
from handlers.user.main_menu.menu import user__main_menu
from utils.redis_models.user_data import UserModel, GroupInfoModel


async def college_group__input(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    """
    Получает введенную группу, если такая есть, то добавляем нового cтудента.
    :param message:
    :param state:
    :param session_pool:
    :param redis__db_1:
    :return:
    """
    logging.info("Добавляю нового студента.")
    users, college_groups = await redis__db_1.get_multiple_data('users', 'college_groups')
    users_data = users.get('users_data')
    user_id = str(message.from_user.id)
    college_group = message.text

    if college_group in college_groups['Туполева,17а']:
        college_building = 'Туполева,17а'
    elif college_group in college_groups['Курчатова,16']:
        college_building = 'Курчатова,16'
    else:
        await message.answer(BotErrors.college_group_not_found)
        logging.error("Ошибка при добавлении нового студента "
                      f"| User [{user_id}] | input [{college_group}] | mgs [{BotErrors.college_group_not_found}]")
        return

    user_model = UserModel(
        current_group=GroupInfoModel(
            college_building=college_building,
            group=college_group
        ),
        default_college_group=college_group,
        default_college_building=college_building
    )
    users_data[user_id] = user_model.dict()
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