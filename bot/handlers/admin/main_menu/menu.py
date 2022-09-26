import logging

from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from keyboards.reply_keyboard_markup import main_menu_markup
from states.admin_state_machine import MainMenuStates
from utils.jsons.work_with_json import read_json


async def admin__main_menu(message: Message, state: FSMContext):
    """
    Главное меню админа бота. Если user_id есть в owner.json, то добавляется кнопка для смены роли.
    :param message:
    :param state:
    :return:
    """
    logging.info(f"User [{message.from_user.id}] перешел в admin menu")
    reply_markup = main_menu_markup(role='Admin')
    owners = read_json('owners.json')
    if message.from_user.id in owners:
        reply_markup = main_menu_markup(role='Admin', alter_role=True)

    await message.answer(BotMessages.admin__main_menu, reply_markup=reply_markup)
    await state.set_state(MainMenuStates.main_menu)
