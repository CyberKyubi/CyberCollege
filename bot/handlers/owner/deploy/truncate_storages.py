from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from states.owner_state_machine import DeployStates
from keyboards.reply_keyboard_markup import reply_markup
from storages.redis.storage import RedisStorage
from storages.db.requests import truncate__tables
from .deploy import deploy__section


async def confirm_your_action__send_buttons(message: Message, state: FSMContext):
    await message.answer(
        BotMessages.confirm_your_action.format(action=BotMessages.truncate_storages__action),
        reply_markup=reply_markup('confirm_your_action')
    )
    await state.set_state(DeployStates.confirm_your_action)


async def confirm_your_action__input(
        message: Message,
        state: FSMContext,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    if message.text == BotButtons.yes:
        await truncate_storages(message, state, session_pool, redis__db_1, redis__db_2)
    elif message.text == BotButtons.no or message.text == BotButtons.back:
        await deploy__section(message, state)


async def truncate_storages(
        message: Message,
        state: FSMContext,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    await truncate__tables(session_pool)

    await redis__db_1.delete_all_data()
    await redis__db_2.delete_all_data()

    await message.answer(BotMessages.storages_cleared)
    await deploy__section(message, state)


def register_truncate_storages(dp: Dispatcher):
    dp.register_message_handler(
        confirm_your_action__send_buttons,
        text=BotButtons.truncate_storages,
        state=DeployStates.deploy
    )
    dp.register_message_handler(
        confirm_your_action__input,
        text=BotButtons.confirm_your_action__markup,
        state=DeployStates.confirm_your_action
    )