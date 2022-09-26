import asyncio
import datetime
import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import back_markup
from states.admin_state_machine import AdminTimetableSectionStates
from handlers.admin.main_menu.menu import admin__main_menu
from utils.timatable.timetable import Timetable
from utils.validation.send_message import send_message
from storages.redis.storage import RedisStorage


async def new_timetable__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.send_new_timetable, reply_markup=back_markup())
    await state.set_state(AdminTimetableSectionStates.new_timetable)


async def preparing(files: dict, message: Message, state: FSMContext, redis__db_1: RedisStorage, redis__db_2):
    """
    Добавляет новое расписание.
    :param files: словарь с путями к загруженным файлам.
    :param message:
    :param state:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    college_groups__redis = await redis__db_1.get_data('college_groups')
    college_groups__excel = {}

    logging.info("Собираю информацию об расписании.")
    # Собирает информацию об расписании. #
    college_buildings, dates = {}, {}
    paths = list(files.values())
    for path in paths:
        cls = Timetable(path)
        excel, _ = cls.get_groups()
        college_groups__excel.update(excel)

        info, dates = cls.get_info_about_file()
        college_buildings.update(info), dates.update(dates)

    logging.info("Ищу разницу между сохраненными группами и группами из файлов расписания.")
    # Ищет разницу между сохраненными группами и группами из файла расписания.
    # Пока не знаю что с этим делать. #
    new_groups, deleted_groups = [], []
    for college_building, groups in college_groups__excel.items():
        not_in_redis = list(set(groups) - set(college_groups__redis[college_building]))
        not_in_excel = list(set(college_groups__redis[college_building]) - set(groups))
        if not_in_redis:
            new_groups.extend(not_in_redis)
        if not_in_excel:
            deleted_groups.extend(not_in_excel)

    if new_groups or deleted_groups:
        msg = BotMessages.found_difference_between_data.format(
            new=', '.join(new_groups),
            deleted=', '.join(deleted_groups)
        )
        await message.answer(msg)
        logging.info(msg)

    logging.info("Начинаю добавлять расписание.")
    # Добавляет новое расписание. #
    await message.answer(BotMessages.splitting_timetable)
    result = await prepare_new_timetable(message, redis__db_2, college_groups__excel, college_buildings, dates)
    if result:
        await message.answer(BotMessages.timetable_added)
        await admin__main_menu(message, state)

        users = await redis__db_1.get_data('users')
        users_id = users['users_id']

        dates = list(map(lambda date: date.strftime('%d.%m.%Y'), dates.values()))
        msg = BotMessages.new_timetable.format(*dates)
        await asyncio.gather(
            *[send_message(message, msg, int(user_id)) for user_id in users_id]
        )


async def prepare_new_timetable(
        message: Message,
        redis__db_2: RedisStorage,
        college_groups: dict,
        college_buildings: dict,
        dates: dict
):
    """
    Записывает в redis новое расписание.
    :param message:
    :param redis__db_2:
    :param college_groups: словарь с группами.
    :param college_buildings: словарь с информацией о расписании: путь, время расписания.
    :param dates:
    :return:
    """
    old_timetable = await redis__db_2.get_data('timetable')

    new_timetable = await splitting_timetable(college_buildings, college_groups)
    new_start_date, new_end_date = tuple(map(lambda date: date.strftime('%Y.%m.%d'), dates.values()))

    if not old_timetable:
        logging.info(f"Новое расписание добавлено | Дата расписания [{new_start_date} - {new_end_date}]")
        await insert_new_timetable('timetable', new_timetable, new_start_date, new_end_date, redis__db_2)
        return True
    else:
        old_start_date, old_end_date = list(map(str_to_date, old_timetable['dates'].values()))
        # Проверка 1. Если дата нового расписания равна дате расписанию, которое уже есть. #
        if dates['start_date'] == old_start_date and dates['end_date'] == old_end_date:
            await message.answer(BotErrors.timetable_is_already_there)
            return

        # Проверка 2.
        # - Если день недели последнего дня старого расписания меньше четверга,
        # то новое расписание на вторую половину недели.
        # - Если больше четверга, то это расписание на следующую неделю.
        # Четверг - 3
        day_of_week_old_timetable = old_end_date.weekday()
        current_day_of_week = datetime.datetime.now().weekday()

        if day_of_week_old_timetable < 3:
            old_dates = old_timetable.pop('dates')
            logging.info("Обновляю старое расписание.")

            # Думаю, если еще посидеть, подумать, поискать методы, то можно куда лучше обновить словарь с
            # расписанием, но пока пусть будет так. #
            for college_building, timetable in new_timetable.items():
                update_old_timetable = old_timetable[college_building]
                result = tuple(map(update_old_week, timetable.items(), update_old_timetable.items()))
                [update_old_timetable.update(timetable_on_group) for timetable_on_group in result]

            old_dates.update(end_date=new_end_date)
            old_timetable.update(dates=old_dates)

            await redis__db_2.set_data('timetable', old_timetable)
            return True

        # Если текущий день недели больше четверга, но меньше воскресенья, то новое расписание будет записано в
        # timetable_for_new_week. Это нужно, чтобы новое расписание не заменяло старое.
        elif 6 > current_day_of_week > 3:
            logging.info(f"Новое расписание добавлено | Дата расписания [{new_start_date} - {new_end_date}]")
            await insert_new_timetable('timetable_for_new_week', new_timetable, new_start_date, new_end_date,
                                       redis__db_2)
            return True
        else:
            logging.info(f"Новое расписание добавлено | Дата расписания [{new_start_date} - {new_end_date}]")
            await insert_new_timetable('timetable', new_timetable, new_start_date, new_end_date, redis__db_2)
            return True


async def splitting_timetable(college_buildings: dict, college_groups: dict) -> dict:
    """
    Разбивает расписание по группам и собирает в словарь.
    :param college_groups: словарь с группами.
    :param college_buildings: словарь с информацией о расписании: путь, время расписания.
    :return:
    """
    logging.info("Разбиваю словарь по группам.")
    [college_buildings[key].update(college_groups=college_groups) for key, college_groups in college_groups.items()]

    timetable = {}
    for college_building, values in college_buildings.items():
        cls = Timetable(excel_file=values['path'], default_college_building=college_building)
        timetable[college_building] = cls.timetable(values['college_groups'])
    return timetable


def str_to_date(date: str):
    """
    Форматирует строку даты в date type.
    :param date:
    :return:
    """
    date_elem = [int(elem) for elem in date.split('.')]
    return datetime.date(*date_elem)


def update_old_week(new_timetable: tuple, old_timetable: tuple):
    """
    Обновляет старое расписание, добавляя вторую половину недели.
    :param new_timetable:
    :param old_timetable:
    :return:
    """
    group, new_week = new_timetable
    _, old_week = old_timetable

    days = ('Четверг', 'Пятница', 'Суббота')
    old_week.update({day_of_week: timetable for day_of_week, timetable in new_week.items() if day_of_week in days})
    return {group: old_week}


async def insert_new_timetable(key: str, new_timetable: dict, start_date, end_date, redis__db_2: RedisStorage):
    """
    Записывает новое расписание в redis.
    :param key: по которому ключу записать в redis.
    timetable - ключ по умолчанию.
    timetable_for_new_week - расписание на новую неделю.
    :param new_timetable: словарь с новым расписанием.
    :param start_date: строка даты начала расписания.
    :param end_date: строка даты окончания расписания.
    :param redis__db_2:
    :return:
    """
    new_timetable.update(dates=dict(start_date=start_date, end_date=end_date))
    await redis__db_2.set_data(key, new_timetable)


def register_new_timetable(dp: Dispatcher):
    dp.register_message_handler(
        new_timetable__button,
        text=BotButtons.add_timetable,
        state=AdminTimetableSectionStates.timetable
    )
