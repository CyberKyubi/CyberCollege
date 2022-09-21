from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from storages.redis.storage import RedisStorage
from handlers.admin.main_menu.menu import admin__main_menu
from handlers.user.main_menu.menu import user__main_menu
from .owner_mode import owner__main_menu
from handlers.user.get_user_data import get_current_group


async def owner__cmd_start(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    owners_data = await redis__db_1.get_data('owners')
    if not owners_data:
        await owner__main_menu(message, state)
        return

    user_id = message.from_user.id
    owner = owners_data.get(str(user_id))
    if owner:
        role = owner['role']
        if role == 'Admin':
            await admin__main_menu(message, state)
            return

    _, college_group = await get_current_group(user_id, redis__db_1)
    await user__main_menu(message, state, college_group)


def register_owner__cmd_start(dp: Dispatcher):
    dp.register_message_handler(
        owner__cmd_start,
        CommandStart(),
        state='*',
        is_owner=True
    )