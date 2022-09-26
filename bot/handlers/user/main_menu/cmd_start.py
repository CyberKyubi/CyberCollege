import logging

from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from states.user_state_machine import RegistrationStates
from storages.redis.storage import RedisStorage
from handlers.user.main_menu.menu import user__main_menu


async def user__cmd_start(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    users = await redis__db_1.get_data('users')
    users_data = users['users_data']
    users_id = users['users_id']

    # Зарегистрирован ли студент #
    user_id = str(message.from_user.id)
    if user_id not in users_id:
        logging.info(f"User [{message.from_user.id}] впервые зашел в бота!")
        await message.answer(BotMessages.college_group__input, reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.college_group__input)
        return

    college_group = users_data[user_id]['current_group']['group']
    await user__main_menu(message, state, college_group)


def register_user__cmd_start(dp: Dispatcher):
    dp.register_message_handler(
        user__cmd_start,
        CommandStart(),
        state='*'
    )
