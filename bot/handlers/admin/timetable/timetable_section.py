import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import reply_markup
from states.admin_state_machine import MainMenuStates, AdminTimetableSectionStates


async def admin_timetable__section(message: Message, state: FSMContext):
    """
    Раздел для работы с расписанием.
    :param message:
    :param state:
    :return:
    """
    logging.info(f"Admin | {message.from_user.id} | Переход | в раздел [Расписание]")
    await message.answer(BotMessages.admin_timetable__section, reply_markup=reply_markup('admin_timetable'))
    await state.set_state(AdminTimetableSectionStates.timetable)


async def back_to_timetable_section__button(message: Message, state: FSMContext):
    await admin_timetable__section(message, state)


def register_admin_timetable__section(dp: Dispatcher):
    dp.register_message_handler(
        admin_timetable__section,
        text=BotButtons.admin_timetable,
        state=MainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_timetable_section__button,
        text=BotButtons.back_to_timetable_section,
        state=AdminTimetableSectionStates.new_timetable
    )