import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import setting_markup
from states.user_state_machine import MainMenuStates, SettingsSectionStates, ChangeCollegeGroupStates


async def settings__section(message: Message, state: FSMContext):
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Настройки]")
    await message.answer(BotMessages.settings__section, reply_markup=setting_markup())
    await state.set_state(SettingsSectionStates.settings)


async def back_to_settings__button(message: Message, state: FSMContext):
    await settings__section(message, state)


def register_setting__section(dp: Dispatcher):
    dp.register_message_handler(
        settings__section,
        text=BotButtons.settings,
        state=MainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_settings__button,
        text=BotButtons.back_to_settings,
        state=ChangeCollegeGroupStates.menu
    )
    dp.register_message_handler(
        back_to_settings__button,
        text=BotButtons.back_to_settings,
        state=ChangeCollegeGroupStates.add_first_group
    )
    dp.register_message_handler(
        back_to_settings__button,
        text=BotButtons.back_to_settings,
        state=ChangeCollegeGroupStates.new_group__first
    )
    dp.register_message_handler(
        back_to_settings__button,
        text=BotButtons.back_to_settings,
        state=SettingsSectionStates.delete_account
    )
    dp.register_message_handler(
        back_to_settings__button,
        text=BotButtons.back_to_settings,
        state=SettingsSectionStates.feedback
    )