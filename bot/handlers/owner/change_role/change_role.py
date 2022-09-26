from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotButtons, BotMessages
from states.owner_state_machine import OwnerMainMenuStates, ChangeRoleStates
from keyboards.reply_keyboard_markup import reply_markup
from storages.redis.storage import RedisStorage
from handlers.user.main_menu.cmd_start import user__cmd_start
from handlers.admin.main_menu.menu import admin__main_menu
from handlers.owner.main_menu.menu import owner__main_menu
from .set_role import set_current_role
from utils.redis_models.owner import Roles


async def change_role__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.change_role__section, reply_markup=reply_markup('change_role'))
    await state.set_state(ChangeRoleStates.change_role)


async def back_to_main_menu__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await owner__main_menu(message, state, redis__db_1)


async def change_role_to_user(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await set_current_role(str(message.from_user.id), Roles.admin, redis__db_1)
    await user__cmd_start(message, state, redis__db_1)


async def change_role_to_admin(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await set_current_role(str(message.from_user.id), Roles.admin, redis__db_1)
    await admin__main_menu(message, state)


def register_change_role__section(dp: Dispatcher):
    dp.register_message_handler(
        change_role__section,
        text=BotButtons.change_role,
        state=OwnerMainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=ChangeRoleStates.change_role
    )

    dp.register_message_handler(
        change_role_to_user,
        text=BotButtons.user_role,
        state=ChangeRoleStates.change_role,
        is_owner=True
    )
    dp.register_message_handler(
        change_role_to_admin,
        text=BotButtons.admin_role,
        state=ChangeRoleStates.change_role,
        is_owner=True
    )