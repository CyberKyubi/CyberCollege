import logging

from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.dispatcher.storage import FSMContext

from keyboards.reply_keyboard_markup import reply_markup
from locales.ru import BotButtons, BotMessages
from keyboards.inline_keyboard_markup import go_to_new_timetable_cd
from states.user_state_machine import UserTimetableSectionStates
from storages.redis.storage import RedisStorage


async def go_to_new_timetable__button(
        query: CallbackQuery,
        state: FSMContext,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    """
    Обрабатывает кнопку в уведомлении о новом расписании.
    :param query:
    :param state:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    logging.info(f"User | {query.from_user.id} | Расписание пар | [Кликнул по кнопке нового расписания в уведомлении]")
    users = await redis__db_1.get_data('users')
    timetable_for_new_week = await redis__db_2.get_data('timetable_for_new_week')
    if timetable_for_new_week:
        selected_timetable = 'new_timetable'
    else:
        selected_timetable = 'timetable'

    users['users_data'][str(query.from_user.id)].update(selected_timetable=selected_timetable)
    await redis__db_1.set_data('users', users)

    await query.message.answer(BotMessages.user_timetable__section, reply_markup=reply_markup('user_timetable'))
    await state.set_state(UserTimetableSectionStates.timetable)


def register_go_to_new_timetable(dp: Dispatcher):
    dp.register_callback_query_handler(
        go_to_new_timetable__button,
        go_to_new_timetable_cd.filter(button=BotButtons.go_to_new_timetable),
        state='*'
    )