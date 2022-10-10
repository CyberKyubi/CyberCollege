import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import main_menu_markup
from states.user_state_machine import MainMenuStates, SettingsSectionStates, UserTimetableSectionStates
from utils.jsons.work_with_json import read_json
from storages.redis.storage import RedisStorage
from handlers.user.get_user_data import get_current_group


async def user__main_menu(message: Message, state: FSMContext, college_group: str):
    """
    Главное меню user role. Если user_id есть в owner.json, то добавляется кнопка для смены роли.
    :param message:
    :param state:
    :param college_group:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Главное меню]")
    reply_markup = main_menu_markup()
    owners = read_json('owners.json')
    if message.from_user.id in owners:
        reply_markup = main_menu_markup(alter_role=True)

    await message.answer(BotMessages.user__main_menu.format(college_group=college_group), reply_markup=reply_markup)
    await state.set_state(MainMenuStates.main_menu)


async def back_to_main_menu__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    _, college_group = await get_current_group(message.from_user.id, redis__db_1)
    await user__main_menu(message, state, college_group)


def register_user__main_menu(dp: Dispatcher):
    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=SettingsSectionStates.settings
    )
    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=UserTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=UserTimetableSectionStates.select_timetable
    )