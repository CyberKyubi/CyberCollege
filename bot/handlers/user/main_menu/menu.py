from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from config import load_config
from locales.ru import BotMessages
from keyboards.reply_keyboard_markup import main_menu_markup
from states.user_state_machine import MainMenuStates


async def user__main_menu(message: Message, state: FSMContext, college_group: str):
    reply_markup = main_menu_markup()
    if message.from_user.id in load_config().tgbot.owners_id:
        reply_markup = main_menu_markup(alter_role=True)

    await message.answer(BotMessages.user__main_menu.format(college_group=college_group), reply_markup=reply_markup)
    await state.set_state(MainMenuStates.main_menu)

