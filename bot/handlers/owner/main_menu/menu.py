import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import reply_markup
from states.owner_state_machine import OwnerMainMenuStates
from states.user_state_machine import MainMenuStates as AdminStates
from states.admin_state_machine import MainMenuStates as UserStates
from storages.redis.storage import RedisStorage
from handlers.owner.change_role.set_role import set_current_role
from utils.redis_models.owner import Roles


async def owner__main_menu(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Главное меню owner role.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"Owner [{message.from_user.id}] | перешел в owner__main_menu.")
    await set_current_role(str(message.from_user.id), Roles.owner, redis__db_1)

    await message.answer(BotMessages.owner__main_menu, reply_markup=reply_markup('owner__main_menu'))
    await state.set_state(OwnerMainMenuStates.main_menu)


def register_owner__main_menu(dp: Dispatcher):
    dp.register_message_handler(
        owner__main_menu,
        text=BotButtons.owner_role,
        state=AdminStates.main_menu,
        is_owner=True
    )
    dp.register_message_handler(
        owner__main_menu,
        text=BotButtons.owner_role,
        state=UserStates.main_menu,
        is_owner=True
    )