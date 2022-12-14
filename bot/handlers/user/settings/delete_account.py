import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import reply_markup
from states.user_state_machine import SettingsSectionStates
from handlers.user.settings.settings import settings__section
from handlers.user.main_menu.cmd_start import user__cmd_start
from storages.redis.storage import RedisStorage
from storages.db.requests import delete_user


async def confirm_delete_account__send_buttons(message: Message, state: FSMContext):
    """
    Отправляет подтверждение на уделения себя из бота.
    :param message:
    :param state:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Удалить аккаунт]")
    await message.answer(BotMessages.delete_account, reply_markup=reply_markup('delete_account'))
    await state.set_state(SettingsSectionStates.delete_account)


async def confirm_delete_account__input(
        message: Message,
        state: FSMContext,
        session_pool,
        redis__db_1: RedisStorage,
        dp: Dispatcher
):
    """
    Обрабатывает вывод студента.
    :param message:
    :param state:
    :param session_pool:
    :param redis__db_1:
    :param dp:
    :return:
    """
    user_id__int = message.from_user.id
    if message.text == BotButtons.delete_account__no:
        logging.info(f"User | {message.from_user.id} | Действие | [Удалить аккаунт] > Ответ [Нет]")
        await settings__section(message, state)
    elif message.text == BotButtons.delete_account__yes:
        logging.info(f"User | {message.from_user.id} | Действие | [Удалить аккаунт] > Ответ [Да]")
        await message.answer(BotMessages.deleted_account)
        await delete_student(session_pool, redis__db_1, dp, user_id__int)
        await user__cmd_start(message, state, redis__db_1)


async def delete_student(session_pool, redis__db_1: RedisStorage, dp: Dispatcher, user_id: int):
    """
    Удаляет студента из всех хранилищ.
    :param session_pool:
    :param redis__db_1:
    :param dp:
    :param user_id:
    :return:
    """
    user_id__int = user_id
    user_id__str = str(user_id__int)

    # Database #
    await delete_user(session_pool, user_id__int)

    # Redis #
    await redis__db_1.delete_user(user_id__str)

    # FSM #
    await dp.storage.finish(chat=user_id__int)
    await dp.storage.reset_state(chat=user_id__int, with_data=True)

    logging.info(f"User | {user_id__str} | Действие | [Удален из бота]")


def register_delete_account(dp: Dispatcher):
    dp.register_message_handler(
        confirm_delete_account__send_buttons,
        text=BotButtons.delete_account,
        state=SettingsSectionStates.settings
    )

    dp.register_message_handler(
        confirm_delete_account__input,
        text=[BotButtons.delete_account__yes, BotButtons.delete_account__no],
        state=SettingsSectionStates.delete_account
    )
