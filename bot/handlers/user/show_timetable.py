import datetime

from aiogram import Dispatcher
from aiogram.types import Message

from locales.ru import BotMessages, BotButtons, BotErrors
from states.state_machine import UserStates
from storages.redis.storage import RedisStorage
from storages.db.requests import select__user_data
from vkbot.timetable import Timetable
from config import load_config


async def timetable_for_today__button(
        message: Message,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    college_group = await get_college_group(message.from_user.id, session_pool, redis__db_1)
    timetable = Timetable(load_config().excel_file, college_group).prepare_dataframe()
    await redis__db_2.set_data('timetable', {college_group: timetable})

    timetable_data = await redis__db_2.get_data('timetable')
    timetable = timetable_data[college_group]

    current_day_of_week = number_to_day_of_week(datetime.datetime.now().weekday())
    if current_day_of_week == 'Воскресенье':
        await message.answer(BotErrors.day_of_week_is_sunday.format(when=BotMessages.today__when))
        return

    if isinstance(timetable[current_day_of_week], dict):
        await message.answer(BotMessages.weekend__when.format(when=BotMessages.today__when))
        return

    msg = generate_msg(timetable[current_day_of_week])
    await message.answer(BotMessages.college_group.format(college_group) + msg)


async def timetable_for_tomorrow__button(
        message: Message,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    college_group = await get_college_group(message.from_user.id, session_pool, redis__db_1)
    timetable_data = await redis__db_2.get_data('timetable')
    timetable = timetable_data[college_group]

    current_day_of_week = datetime.datetime.now().weekday()
    day_of_week_for_tomorrow = number_to_day_of_week(current_day_of_week + 1 if current_day_of_week != 6 else 0)
    if day_of_week_for_tomorrow == 'Воскресенье':
        await message.answer(BotErrors.day_of_week_is_sunday.format(when=BotMessages.tomorrow__when))
        return

    if not timetable[day_of_week_for_tomorrow]:
        await message.answer(BotErrors.timetable_not_found)
        return

    if isinstance(timetable[day_of_week_for_tomorrow], dict):
        await message.answer(BotMessages.weekend__when.format(when=BotMessages.tomorrow__when))
        return

    msg = generate_msg(timetable[day_of_week_for_tomorrow])
    await message.answer(BotMessages.college_group.format(college_group) + msg)


async def timetable_for_week__button(
        message: Message,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    college_group = await get_college_group(message.from_user.id, session_pool, redis__db_1)
    timetable_data = await redis__db_2.get_data('timetable')
    timetable = timetable_data[college_group]

    week = ''
    for day_of_week, study_days in timetable.items():
        if study_days:
            if isinstance(study_days, dict):
                day = BotMessages.day_of_week.format(
                    day_of_week=day_of_week, date_str=study_days['date_str']
                ) + study_days['msg'] + '\n\n'
            else:
                day = generate_msg(study_days)
            separator = '_' * 40
            week += separator + '\n\n' + day

    await message.answer(BotMessages.college_group.format(college_group) + week)


async def get_college_group(user_id: int, session_pool, redis__db_1: RedisStorage):
    users = await redis__db_1.get_data('users')
    users_data = users['users_data']

    user_id__str = str(user_id)
    user_data = users_data.get(user_id__str)
    if not user_data:
        college_group = await select__user_data(session_pool, user_id)
        users.update({user_id__str: {'college_group': college_group}})
        await redis__db_1.set_data('users', users)
    else:
        college_group = user_data['college_group']
    return college_group


def month_name_to_number(month_name_raw: str) -> int:
    month_name = month_name_raw.strip().capitalize()
    months = {'Сентября': 9, 'Ноября': 10, 'Октября': 11, 'Декабря': 12, 'Января': 1, 'Февраля': 2, 'Марта': 3,
              'Апреля': 4, 'Мая': 5, 'Июня': 6, 'Июля': 7}
    return months[month_name]


def number_to_day_of_week(number: int):
    week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    return week[number]


def generate_msg(timetable: dict) -> str:
    msg = ''
    date = {}
    for item in timetable:
        date.update(day_of_week=item['day_of_week'], date_str=item['date_str'])
        msg += BotMessages.timetable_for_one_day.format(**item)
    return BotMessages.day_of_week.format(**date) + msg


def register_show_timetable(dp: Dispatcher):
    dp.register_message_handler(
        timetable_for_today__button,
        text=BotButtons.timetable_for_today,
        state=UserStates.main_menu
    )
    dp.register_message_handler(
        timetable_for_tomorrow__button,
        text=BotButtons.timetable_for_tomorrow,
        state=UserStates.main_menu
    )
    dp.register_message_handler(
        timetable_for_week__button,
        text=BotButtons.timetable_for_week,
        state=UserStates.main_menu
    )