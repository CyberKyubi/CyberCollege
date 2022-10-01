from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import reply_markup
from states.admin_state_machine import MainMenuStates, AdminTimetableSectionStates
from handlers.admin.main_menu.menu import admin__main_menu


async def admin_timetable__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.admin_timetable__section, reply_markup=reply_markup('admin_timetable'))
    await state.set_state(AdminTimetableSectionStates.timetable)


async def back_to_main_menu__button(message: Message, state: FSMContext):
    await admin__main_menu(message, state)


async def back_to_timetable_section__button(message: Message, state: FSMContext):
    await admin_timetable__section(message, state)


def register_admin_timetable__section(dp: Dispatcher):
    dp.register_message_handler(
        admin_timetable__section,
        text=BotButtons.admin_timetable,
        state=MainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=AdminTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        back_to_timetable_section__button,
        text=BotButtons.back_to_timetable_section,
        state=AdminTimetableSectionStates.new_timetable
    )