import asyncio
import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup
from states.admin_state_machine import AdminTimetableSectionStates, TimetableChangesStates
from handlers.admin.main_menu.menu import admin__main_menu
from handlers.user.timetable.timetable_of_classes import generate_weekend, generate_study_day
from .timetable_section import admin_timetable__section
from .download_file import get_path
from .new_timetable import splitting_timetable
from utils.timatable.timetable import Timetable
from utils.validation.send_message import send_message
from utils.redis_models.timetable_changes import TimetableChangesModel
from utils.redis_models.timetable import TimetableModel, Status
from utils.redis_models.user_data import UserModel
from storages.redis.storage import RedisStorage
from config_reader import config


async def timetable_changes__section(message: Message, state: FSMContext):
    """
    Раздел с изменением расписания. Отправляет выбор кол-во корпусов, у которых изменения в расписании.
    :param message:
    :param state:
    :return:
    """
    logging.info(f"Admin | {message.from_user.id} | Переход | в раздел [Изменения в расписании]")
    await message.answer(BotMessages.timetable_changes_in, reply_markup=reply_markup('timetable_changes'))
    await state.set_state(TimetableChangesStates.number_of_college_building)


async def back_to_timetable_section(message: Message, state: FSMContext):
    await admin_timetable__section(message, state)


async def back_to_choice_college_building__button(message: Message, state: FSMContext, redis__db_2: RedisStorage):
    """
    Возвращает к выбору корпуса.
    :param message:
    :param state:
    :param redis__db_2:
    :return:
    """
    timetable_changes_data = await redis__db_2.get_data('timetable_changes')
    model = TimetableChangesModel(**timetable_changes_data)

    msg = BotMessages.admin_choice_college_building
    if model.number_of_college_building == 2:
        msg = BotMessages.choice_first_college_building

    await message.answer(msg, reply_markup=reply_markup('admin_choice_college_building'))
    await state.set_state(TimetableChangesStates.choice_college_building)


async def number_of_college_building__input(message: Message, state: FSMContext, redis__db_2: RedisStorage):
    """
    Получает кол-во корпусов, у которых изменения в расписании.
    :param message:
    :param state:
    :param redis__db_2:
    :return:
    """
    number_of_college_building = 1
    msg = BotMessages.admin_choice_college_building
    if message.text == BotButtons.two_college_building:
        number_of_college_building = 2
        msg = BotMessages.choice_first_college_building

    model = TimetableChangesModel(number_of_college_building=number_of_college_building)
    await redis__db_2.set_data('timetable_changes', model.dict())
    logging.info(f"Admin | {message.from_user.id} | Действие | выбрал [Кол-во корпусов, у которых изменения] "
                 f"-> {number_of_college_building}")

    await message.answer(msg, reply_markup=reply_markup('admin_choice_college_building'))
    await state.set_state(TimetableChangesStates.choice_college_building)


async def choose_college_building__input(message: Message, state: FSMContext, redis__db_2: RedisStorage):
    """
    Обрабатывает выбор корпуса. Если кол-во корпусов равно 2, то записывает первый корпус.
    :param message:
    :param state:
    :param redis__db_2:
    :return:
    """
    timetable_changes_data = await redis__db_2.get_data('timetable_changes')
    model = TimetableChangesModel(**timetable_changes_data)

    without_emoji = message.text[2:]
    timetable_changes_data['first_college_buildings'] = without_emoji
    await redis__db_2.set_data('timetable_changes', timetable_changes_data)
    logging.info(f"Admin | {message.from_user.id} | Действие | выбрал [Корпус] -> {without_emoji}")

    msg = BotMessages.send_timetable_changes
    next_state = TimetableChangesStates.one_college_building
    if model.number_of_college_building == 2:
        next_state = TimetableChangesStates.two_college_building
        msg = BotMessages.send_first_timetable_changes

    await message.answer(msg, reply_markup=reply_markup('back_to_choose_college_building', back=True))
    await state.set_state(next_state)


async def one_college_building__input(message: Message, state: FSMContext, redis__db_1, redis__db_2: RedisStorage):
    """
    Для одного корпуса. Скачивает полученный документ.
    :param message:
    :param state:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    logging.info(f'Admin | {message.from_user.id} | Действие | отправил [файл 1/1]')
    timetable_changes_data = await redis__db_2.get_data('timetable_changes')
    model = TimetableChangesModel(**timetable_changes_data)

    path = await get_path(message, config.timetable_changes_1)
    model.college_buildings_info.update({model.first_college_buildings: {'path': path}})
    await timetable_changes(message, state, model, redis__db_1, redis__db_2)


async def two_college_building__input(message: Message, state: FSMContext, redis__db_1, redis__db_2: RedisStorage):
    """
    Для двух корпусов. Скачивает полученный документ.
    Если нет данных, то записываем первый файл.
    :param message:
    :param state:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    timetable_changes_data = await redis__db_2.get_data('timetable_changes')
    model = TimetableChangesModel(**timetable_changes_data)

    if not model.college_buildings_info:
        logging.info(f'Admin | {message.from_user.id} | Действие | отправил [файл 1/2]')
        path = await get_path(message, config.timetable_changes_1)
        model.college_buildings_info.update({model.first_college_buildings: {'path': path}})
        await redis__db_2.set_data('timetable_changes', model.dict())

        await message.answer(
            BotMessages.send_second_timetable,
            reply_markup=reply_markup('back_to_choose_college_building', back=True)
        )
        await state.set_state(TimetableChangesStates.two_college_building)
    else:
        logging.info(f'Admin | {message.from_user.id} | Действие | отправил [файл 2/2]')
        path = await get_path(message, config.timetable_changes_2)
        college_building = 'Курчатова,16'
        if model.first_college_buildings == college_building:
            college_building = 'Туполева,17а'
        model.college_buildings_info.update({college_building: {'path': path}})
        await timetable_changes(message, state, model, redis__db_1, redis__db_2)


async def timetable_changes(
        message: Message,
        state: FSMContext,
        model: TimetableChangesModel,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    """
    Вносит изменение в текущее расписание.
    :param message:
    :param state:
    :param model:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    logging.debug(f'BOT | Действие | начало [Внесение изменений в текущее расписание]')
    college_groups = {}
    path = ''
    for co_bld, value in model.college_buildings_info.items():
        path = value['path']
        redis, _ = Timetable(path, co_bld).get_groups()
        college_groups.update(redis)

    # Сокращения для этой функции
    # tt - timetable
    # new_tt_dt - new timetable data
    # old_tt_dt - old timetable data
    # tt_ch_dt - timetable_changes_data
    # gp - group
    # tt_gp - timetable for group
    # tt_day - timetable for day
    # co_bld - college building
    # day_w - day of week
    try:
        new_tt_dt = await splitting_timetable(model.college_buildings_info, college_groups, timetable_changes=True)
        _, dates = Timetable(path).dates_of_timetable()
        dates__str = generate_date_str(dates)
    except Exception as error:
        logging.error(error)
        await message.answer(BotErrors.error_in_timetable)
    else:
        old_tt_dt = await redis__db_2.get_data('timetable')
        tt_ch_dt = {}
        groups = []
        changes = False

        for co_bld, new_tt_gp in new_tt_dt.items():
            for gp, tt in new_tt_gp.items():
                old_tt_gp = old_tt_dt[co_bld].get(gp)
                # Проверка на появление групп, которых не было в основном расписании. #
                if old_tt_gp:
                    day_w = list(tt.keys())[0]

                    new_tt_day, old_tt_day = tt[day_w], old_tt_gp[day_w]
                    model_new_tt, model_old_tt = TimetableModel(**new_tt_day), TimetableModel(**old_tt_day)
                    new_tt, old_tt = new_tt_day['timetable'], old_tt_day['timetable']
                    if new_tt != old_tt:
                        changes = True
                        tt_string = generate_timetable_string(
                            timetables=((model_new_tt, new_tt, 'new_timetable'), (model_old_tt, old_tt, 'old_timetable')),
                            day_of_week=day_w, group=gp, dates=dates__str
                        )

                        groups.append(gp)
                        tt_ch_dt.update({gp: tt_string})
                        old_tt_gp.update(tt)

        if changes:
            await redis__db_2.set_data('timetable', old_tt_dt)
            logging.debug(f'BOT | Действие | конец [Изменения в расписание внесены]')
            await message.answer(BotMessages.timetable_changes_saved)
            await admin__main_menu(message, state)

            await notify_about_timetable_changes(message, redis__db_1, tt_ch_dt, groups, dates__str)
        else:
            logging.debug(f'BOT | Действие | конец [Изменения в расписание не сохранены]')
            await message.answer(BotMessages.timetable_changes_not_saved)
            await admin__main_menu(message, state)


async def notify_about_timetable_changes(
        message: Message,
        redis__db_1: RedisStorage,
        timetable_changes_data: dict,
        groups: list,
        dates: str
):
    """
    Отправляет уведомление о новом расписании студентам из группы, у которой изменения, и друзьям у кого эта
    группа добавлена.
    :param message:
    :param redis__db_1:
    :param timetable_changes_data: Словарь разбитый по группам, в которых лежит строка нового и старого расписания.
    :param groups: Список групп, у которых изменения в расписании.
    :param dates:
    :return:
    """
    logging.debug(f'BOT | Действие | начало [Уведомить об изменениях в расписании]')
    users = await redis__db_1.get_data('users')
    users_data = users['users_data']

    for user_id, user_data in users_data.items():
        model = UserModel(**user_data)
        if model.default_college_group in groups:
            timetable = timetable_changes_data[model.default_college_group]
            await asyncio.gather(
                send_message(message, timetable['new_timetable'], user_id),
                send_message(message, timetable['old_timetable'], user_id)
            )

        groups_friends = [groups_friends.group for groups_friends in model.groups_friends if groups_friends.group in groups]
        if groups_friends:
            await send_message(
                message=message,
                user_id=user_id,
                message_to_send=BotMessages.timetable_changes_for_friends.format(
                    date_str=dates, groups=', '.join(groups_friends)
                )
            )
    logging.debug(f'BOT | Действие | конец [Студенты получили уведомление об изменениях в расписании]')


def generate_timetable_string(
        timetables: tuple[tuple[TimetableModel, list, str], tuple[TimetableModel, list, str]],
        day_of_week: str,
        group: str,
        dates: str
) -> dict:
    """
    Генерирует строку расписания на день.
    :param timetables: Кортеж из двух расписания: первое - новое, второе - старое.
    :param day_of_week: День недели. Пример "Понедельник".
    :param group: Группа.
    :param dates:
    :return: Словарь разбитый по группам, в которых лежит строка нового и старого расписания.
    """
    changes = {}
    for model, timetable, key in timetables:
        status = BotMessages.new_timetable if key == 'new_timetable' else BotMessages.old_timetable
        info = BotMessages.warning_timetable_changes.format(date_str=dates) if key == 'old_timetable' else ''

        args = (day_of_week, model.date_str)
        day = generate_study_day(timetable=timetable, *args) if model.status == Status.study_day \
            else generate_weekend(*args)
        msg = status + BotMessages.college_group.format(group) + day + info
        changes.update({key: msg})
    return changes


def generate_date_str(dates: list) -> str:
    dates__str = list(map(lambda date: date.strftime('%d.%m.%Y'), dates))
    match len(dates__str):
        case 2:
            text = BotMessages.date_str__from_to.format(dates__str[0], dates__str[-1])
        case 1:
            text = BotMessages.date_str__one_day.format(dates__str[0])
        case _:
            text = ''
    return text


def register_timetable_changes__section(dp: Dispatcher):
    dp.register_message_handler(
        timetable_changes__section,
        text=BotButtons.timetable_changes,
        state=AdminTimetableSectionStates.timetable
    )

    dp.register_message_handler(
        back_to_timetable_section,
        text=BotButtons.back_to_timetable_section,
        state=TimetableChangesStates.number_of_college_building
    )
    dp.register_message_handler(
        back_to_timetable_section,
        text=BotButtons.back_to_timetable_section,
        state=TimetableChangesStates.choice_college_building
    )
    dp.register_message_handler(
        back_to_choice_college_building__button,
        text=BotButtons.back_to_choice_college_building,
        state=TimetableChangesStates.one_college_building
    )
    dp.register_message_handler(
        back_to_choice_college_building__button,
        text=BotButtons.back_to_choice_college_building,
        state=TimetableChangesStates.two_college_building
    )

    dp.register_message_handler(
        number_of_college_building__input,
        text=[BotButtons.one_college_building, BotButtons.two_college_building],
        state=TimetableChangesStates.number_of_college_building
    )
    dp.register_message_handler(
        choose_college_building__input,
        text=[BotButtons.college_building_1, BotButtons.college_building_2],
        state=TimetableChangesStates.choice_college_building
    )
    dp.register_message_handler(
        one_college_building__input,
        content_types=['document'],
        state=TimetableChangesStates.one_college_building
    )
    dp.register_message_handler(
        two_college_building__input,
        content_types=['document'],
        state=TimetableChangesStates.two_college_building
    )
