import asyncio
import datetime

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup, back_markup
from states.admin_state_machine import MainMenuStates, AdminTimetableSectionStates
from handlers.admin.main_menu.menu import admin__main_menu
from utils.timatable.timetable import Timetable
from utils.validation.send_message import send_message
from storages.redis.storage import RedisStorage
from config import load_config


async def admin_timetable__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.admin_timetable__section, reply_markup=reply_markup('admin_timetable'))
    await state.set_state(AdminTimetableSectionStates.timetable)


async def back_to_main_menu__button(message: Message, state: FSMContext):
    await admin__main_menu(message, state)


async def back__button(message: Message, state: FSMContext):
    await admin_timetable__section(message, state)


async def new_timetable__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.send_new_timetable, reply_markup=back_markup())
    await state.set_state(AdminTimetableSectionStates.new_timetable)


async def new_timetable__input(
        message: Message,
        state: FSMContext,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage,
        album: list
):
    if len(album) == 1:
        await message.answer(BotErrors.received_one_excel_file)
        return

    # Скачивание файлов. #
    paths = [load_config().excel_file_1, load_config().excel_file_2]
    finished, _ = await asyncio.wait(
        [download_file(message, document.file_id, path) for document, path in zip(album, paths)]
    )

    # Получаем информацию об расписании. #
    paths = [task.result() for task in finished]
    college_buildings, dates = {}, {}
    for path in paths:
        info, dates = Timetable(path).get_info_about_file()
        college_buildings.update(info), dates.update(dates)

    await message.answer(BotMessages.received_excel_files)
    result = await prepare_new_timetable(message, redis__db_1, redis__db_2, college_buildings, dates)
    # Эта проверка нужна, чтобы дождаться добавления нового расписания. #
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
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage,
        college_buildings: dict,
        dates: dict
):
    college_groups = await redis__db_1.get_data('college_groups')
    old_timetable = await redis__db_2.get_data('timetable')

    new_timetable = await splitting_timetable(college_buildings, college_groups)
    new_start_date, new_end_date = tuple(map(lambda date: date.strftime('%Y.%m.%d'), dates.values()))

    if not old_timetable:
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

            # Думаю, если еще посидеть, подумать, поискать методы, то можно куда лучше обновить словарь с
            # расписанием, но пока пусть будет так. #
            for college_building, timetable in new_timetable.items():
                update_old_timetable = old_timetable[college_building]
                result = tuple(map(update_old_week, timetable.items(), update_old_timetable.items()))
                [update_old_timetable.update(timetable_on_group) for timetable_on_group in result if timetable_on_group]

            old_dates.update(end_date=new_end_date)
            old_timetable.update(dates=old_dates)

            await redis__db_2.set_data('timetable', old_timetable)
            return True

        # Если текущий день недели больше четверга, но меньше воскресенья, то новое расписание будет записано в
        # timetable_for_new_week. Это нужно, чтобы новое расписание не заменяло старое.
        elif 6 > current_day_of_week > 3:
            await insert_new_timetable('timetable_for_new_week', new_timetable, new_start_date, new_end_date, redis__db_2)
            return True
        else:
            await insert_new_timetable('timetable', new_timetable, new_start_date, new_end_date, redis__db_2)
            return True


async def insert_new_timetable(key: str, new_timetable: dict, start_date, end_date, redis__db_2: RedisStorage):
    new_timetable.update(dates=dict(start_date=start_date, end_date=end_date))
    await redis__db_2.set_data(key, new_timetable)


def str_to_date(date: str):
    date_elem = [int(elem) for elem in date.split('.')]
    return datetime.date(*date_elem)


def update_old_week(new_timetable: tuple, old_timetable: tuple):
    group, new_week = new_timetable
    _, old_week = old_timetable

    if not old_week:
        return

    days = ('Четверг', 'Пятница', 'Суббота')
    old_week.update({day_of_week: timetable for day_of_week, timetable in new_week.items() if day_of_week in days})
    return {group: old_week}


async def download_file(message: Message, file_id: str, path: str):
    await message.bot.download_file_by_id(file_id, path)
    return path


async def splitting_timetable(college_buildings: dict, college_groups: dict) -> dict:
    [college_buildings[key].update(college_groups=college_groups) for key, college_groups in college_groups.items()]

    timetable = {}
    for college_building, values in college_buildings.items():
        cls = Timetable(excel_file=values['path'], default_college_building=college_building)
        timetable[college_building] = cls.timetable(values['college_groups'])
    return timetable


def register_admin_timetable__section(dp: Dispatcher):
    dp.register_message_handler(
        admin_timetable__section,
        text=BotButtons.admin_timetable,
        state=MainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=AdminTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=AdminTimetableSectionStates.new_timetable
    )

    dp.register_message_handler(
        new_timetable__button,
        text=BotButtons.add_timetable,
        state=AdminTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        new_timetable__input,
        content_types=['document'],
        state=AdminTimetableSectionStates.new_timetable
    )