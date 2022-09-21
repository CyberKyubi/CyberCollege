from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import reply_markup
from states.user_state_machine import MainMenuStates, SettingsSectionStates
from handlers.user.main_menu.menu import user__main_menu
from handlers.user.get_user_data import get_current_group
from storages.redis.storage import RedisStorage


async def settings__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.settings__section, reply_markup=reply_markup('settings'))
    await state.set_state(SettingsSectionStates.settings)


async def back_to_main_menu__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    _, college_group = await get_current_group(message.from_user.id, redis__db_1)
    await user__main_menu(message, state, college_group)


def register_setting__section(dp: Dispatcher):
    dp.register_message_handler(
        settings__section,
        text=BotButtons.settings,
        state=MainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=SettingsSectionStates.settings
    )