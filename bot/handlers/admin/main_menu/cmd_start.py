from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.admin.main_menu.menu import admin__main_menu


async def admin__cmd_start(message: Message, state: FSMContext):
    await admin__main_menu(message, state)


def register_admin__cmd_start(dp: Dispatcher):
    dp.register_message_handler(
        admin__cmd_start,
        CommandStart(),
        state='*',
        is_admin=True
    )