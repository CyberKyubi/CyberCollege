import logging

from aiogram import Dispatcher
from aiogram.types import Message

from locales.ru import BotMessages, BotButtons
from states.user_state_machine import MainMenuStates


async def timetable_break__button(message: Message):
    logging.info(f"User | {message.from_user.id} | Действие | [Показать расписание перемен]")
    await message.answer(BotMessages.break_timetable)


def register_break_timetable(dp: Dispatcher):
    dp.register_message_handler(
        timetable_break__button,
        text=BotButtons.break_timetable,
        state=MainMenuStates.main_menu,
    )