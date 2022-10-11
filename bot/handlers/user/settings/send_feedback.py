import asyncio
import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup
from states.user_state_machine import SettingsSectionStates
from storages.redis.storage import RedisStorage
from handlers.user.settings.settings import settings__section
from handlers.user.get_user_data import get_default_values
from utils.validation.get_mention import get_mention
from utils.validation.send_message import send_message
from config_reader import config


async def send_feedback__section(message: Message, state: FSMContext):
    """
    Раздел с feedback'ом.
    :param message:
    :param state:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Отправить feedback]")
    await message.answer(BotMessages.send_feedback__section, reply_markup=reply_markup('send_feedback'))
    await state.set_state(SettingsSectionStates.feedback)


async def back__button(message: Message, state: FSMContext):
    await send_feedback__section(message, state)


async def private_message__button(message: Message, redis__db_1: RedisStorage):
    """
    Отправляет сервисный тг аккаунт.
    :param message:
    :param redis__db_1:
    :return:
    """
    user_id = message.from_user.id
    college_group, college_building = await get_default_values(user_id, redis__db_1)
    await message.answer(BotMessages.private_message)
    logging.info(f'User | {message.from_user.id} | Действие | [Получил мой сервисный аккаунт тг.]')


async def send_message_to_lucifer(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Переводит в раздел, где студент может написать мне сообщение, если студент не throttled.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Написать feedback]")
    user_id = str(message.from_user.id)
    throttled = await redis__db_1.get_throttle_key(user_id)
    if throttled:
        await message.answer(BotErrors.throttled)
        return

    await message.answer(BotMessages.send_message_to_lucifer, reply_markup=reply_markup('back', back=True))
    await state.set_state(SettingsSectionStates.send_message)


async def message_to_send__input(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Получает сообщение от студента и отправляет в сервисный аккаунт.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Действие | [Отправил сообщение]")
    user_id = str(message.from_user.id)
    await redis__db_1.set_throttle_key(user_id)

    await message.answer(BotMessages.message_sent)
    await settings__section(message, state)

    college_group, college_building = await get_default_values(message.from_user.id, redis__db_1)
    username = await get_mention(message, user_id)
    message_from = BotMessages.message_from.format(college_group, college_building, user_id, username)
    doom = config.doom_id
    await asyncio.gather(
        send_message(message, message_to_send=message_from, user_id=doom),
        send_message(message, message_to_send=message.text, user_id=doom)
    )


def register_send_feedback__section(dp: Dispatcher):
    dp.register_message_handler(
        send_feedback__section,
        text=BotButtons.message_to_the_developer,
        state=SettingsSectionStates.settings
    )

    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=SettingsSectionStates.send_message
    )

    dp.register_message_handler(
        private_message__button,
        text=BotButtons.private_message,
        state=SettingsSectionStates.feedback
    )
    dp.register_message_handler(
        send_message_to_lucifer,
        text=BotButtons.from_bot,
        state=SettingsSectionStates.feedback
    )
    dp.register_message_handler(
        message_to_send__input,
        content_types=['text'],
        state=SettingsSectionStates.send_message
    )