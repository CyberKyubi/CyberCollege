from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from storages.redis.storage import RedisStorage
from handlers.admin.main_menu.menu import admin__main_menu
from handlers.user.main_menu.cmd_start import user__cmd_start
from handlers.owner.main_menu.menu import owner__main_menu
from utils.redis_models.owner import OwnerModel, Roles


async def owner__cmd_start(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Обработка команды /start у owner role.
    Забирает текущую роль из redis и вызывает соответствующее главное меню роли.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    owners_data = await redis__db_1.get_data('owners')
    if not owners_data:
        await owner__main_menu(message, state, redis__db_1)
        return

    user_id = message.from_user.id
    owner_model = OwnerModel(**owners_data.get(str(user_id)))

    if owner_model.role == Roles.admin:
        await admin__main_menu(message, state)
    elif owner_model.role == Roles.user:
        await user__cmd_start(message, state, redis__db_1)
    elif owner_model.role == Roles.owner:
        await owner__main_menu(message, state, redis__db_1)


def register_owner__cmd_start(dp: Dispatcher):
    dp.register_message_handler(
        owner__cmd_start,
        CommandStart(),
        state='*',
        is_owner=True
    )