from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from keyboards.reply_keyboard_markup import main_menu_markup
from states.user_state_machine import MainMenuStates
from utils.jsons.work_with_json import read_json


async def user__main_menu(message: Message, state: FSMContext, college_group: str):
    """
    Главное меню user role. Если user_id есть в owner.json, то добавляется кнопка для смены роли.
    :param message:
    :param state:
    :param college_group:
    :return:
    """
    reply_markup = main_menu_markup()
    owners = read_json('owners.json')
    if message.from_user.id in owners:
        reply_markup = main_menu_markup(alter_role=True)

    await message.answer(BotMessages.user__main_menu.format(college_group=college_group), reply_markup=reply_markup)
    await state.set_state(MainMenuStates.main_menu)

