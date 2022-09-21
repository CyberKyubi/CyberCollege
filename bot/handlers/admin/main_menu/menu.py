from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from keyboards.reply_keyboard_markup import main_menu_markup
from states.admin_state_machine import MainMenuStates
from config import load_config


async def admin__main_menu(message: Message, state: FSMContext):
    reply_markup = main_menu_markup(role='Admin')
    if message.from_user.id in load_config().tgbot.owners_id:
        reply_markup = main_menu_markup(role='Admin', alter_role=True)

    await message.answer(BotMessages.admin__main_menu, reply_markup=reply_markup)
    await state.set_state(MainMenuStates.main_menu)
