from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from states.owner_state_machine import OwnerMainMenuStates, DeployStates
from keyboards.reply_keyboard_markup import reply_markup
from storages.redis.storage import RedisStorage
from handlers.owner.main_menu.menu import owner__main_menu


async def deploy__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.deploy__section, reply_markup=reply_markup('deploy__section'))
    await state.set_state(DeployStates.deploy)


async def bact_to_main_menu__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await owner__main_menu(message, state, redis__db_1)


def register_deploy__section(dp: Dispatcher):
    dp.register_message_handler(
        deploy__section,
        text=BotButtons.deploy,
        state=OwnerMainMenuStates.main_menu
    )

    dp.register_message_handler(
        bact_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=DeployStates.deploy
    )