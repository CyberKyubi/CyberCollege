import logging
import datetime

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup, days_of_week_markup
from states.user_state_machine import MainMenuStates, UserTimetableSectionStates
from storages.redis.storage import RedisStorage
from handlers.user.main_menu.menu import user__main_menu
from handlers.user.get_user_data import get_current_group
from utils.redis_models.timetable import TimetableModel, Status


async def select_timetable(message: Message, state: FSMContext, redis__db_2: RedisStorage):
    """
    Если есть новое расписание, то отправляет выбор.
    Если нет, то переходит в раздел расписания.
    :param message:
    :param state:
    :param redis__db_2:
    :return:
    """
    if await timetable_is_new(redis__db_2):
        logging.info(f"User [{message.from_user.id}] | предложен выбор расписания.")
        await message.answer(BotMessages.select_timetable, reply_markup=reply_markup('select_timetable'))
        await state.set_state(UserTimetableSectionStates.select_timetable)
        return
    else:
        await timetable_of_classes__section(message, state)


async def timetable_of_classes__section(message: Message, state: FSMContext):
    """
    Раздел с расписанием пар.
    :param message:
    :param state:
    :return:
    """
    logging.info(f"User [{message.from_user.id}] | перешел в раздел расписания.")
    await message.answer(BotMessages.user_timetable__section, reply_markup=reply_markup('user_timetable'))
    await state.set_state(UserTimetableSectionStates.timetable)


async def back_to_main_menu__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    _, college_group = await get_current_group(message.from_user.id, redis__db_1)
    await user__main_menu(message, state, college_group)


async def back_to_timetable__button(message: Message, state: FSMContext):
    await timetable_of_classes__section(message, state)


async def select_timetable__input(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Обрабатывает выбор расписания.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    selected_timetable = 'timetable'
    if message.text == BotButtons.old_timetable:
        logging.info(f"User [{message.from_user.id}] | выбрал старое расписание.")
        await message.answer(BotMessages.selected_old_timetable)
    if message.text == BotButtons.new_timetable:
        logging.info(f"User [{message.from_user.id}] | выбрал новое расписание.")
        selected_timetable = 'new_timetable'
        await message.answer(BotMessages.selected_new_timetable)

    users = await redis__db_1.get_data('users')
    users['users_data'][str(message.from_user.id)].update(selected_timetable=selected_timetable)
    await redis__db_1.set_data('users', users)

    await message.answer(BotMessages.user_timetable__section, reply_markup=reply_markup('user_timetable'))
    await state.set_state(UserTimetableSectionStates.timetable)


async def timetable_for_today__button(message: Message, redis__db_1: RedisStorage, redis__db_2: RedisStorage):
    """
    Отправляет расписание на сегодня, если все проверки пройдены.
    :param message:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    college_building, college_group, selected_timetable = await get_current_group(
        message.from_user.id, redis__db_1, selected_timetable=True
    )
    new_timetable = await redis__db_2.get_data('timetable_for_new_week')
    key = 'timetable'
    if new_timetable and selected_timetable == 'new_timetable':
        key = 'timetable_for_new_week'
    logging.info(f"User [{message.from_user.id}] | college group [{college_group}] |"
                 f" college building [{college_building}] | timetable [{key}] | расписание [Сегодня]")

    timetable_data = await redis__db_2.get_data(key)
    timetable_for_group = timetable_data[college_building][college_group]
    current_day_of_week = number_to_day_of_week(datetime.datetime.now().weekday())

    # Проверка 1. Если сегодня воскресенье. #
    if current_day_of_week == 'Воскресенье':
        await message.answer(BotErrors.day_of_week_is_sunday.format(when=BotMessages.today__when))
        return

    timetable = timetable_for_group[current_day_of_week]
    timetable_model = TimetableModel(**timetable)

    # Проверка 2. Если расписания нет. #
    if timetable_model.status == Status.unknown:
        await message.answer(BotErrors.still_no_timetable)
        return

    # Проверка 3. Если сегодня выходной. #
    if timetable_model.status == Status.weekend:
        await message.answer(BotMessages.weekend__when.format(when=BotMessages.today__when))
        return

    msg = generate_study_day(current_day_of_week, timetable_model.date_str, timetable['timetable'])
    await message.answer(BotMessages.college_group.format(college_group) + msg)


async def timetable_for_tomorrow__button(message: Message, redis__db_1: RedisStorage, redis__db_2: RedisStorage):
    """
    Отправляет расписание на завтра, если все проверки пройдены.
    :param message:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    college_building, college_group, selected_timetable = await get_current_group(
        message.from_user.id, redis__db_1, selected_timetable=True
    )
    new_timetable = await redis__db_2.get_data('timetable_for_new_week')
    key = 'timetable'
    if new_timetable and selected_timetable == 'new_timetable':
        key = 'timetable_for_new_week'
    logging.info(f"User [{message.from_user.id}] | college group [{college_group}] |"
                 f" college building [{college_building}] | timetable [{key}] | расписание [Завтра]")

    timetable_data = await redis__db_2.get_data(key)
    timetable_for_group = timetable_data[college_building][college_group]

    current_day_of_week = datetime.datetime.now().weekday()
    day_of_week_for_tomorrow = number_to_day_of_week(current_day_of_week + 1 if current_day_of_week != 6 else 0)

    # Проверка 1. Если завтра воскресенье. #
    if day_of_week_for_tomorrow == 'Воскресенье':
        await message.answer(BotErrors.day_of_week_is_sunday.format(when=BotMessages.tomorrow__when))
        return

    timetable = timetable_for_group[day_of_week_for_tomorrow]
    timetable_model = TimetableModel(**timetable)

    # Проверка 2. Если нет нового расписания, а имеющиеся устарело. #
    if not selected_timetable and timetable_is_old(timetable_data['dates']['start_date'], tomorrow=True):
        await message.answer(BotErrors.still_no_timetable)
        return

    # Проверка 3. Если расписания нет. #
    if timetable_model.status == Status.unknown:
        await message.answer(BotErrors.still_no_timetable)
        return

    # Проверка 4. Если завтра выходной. #
    if timetable_model.status == Status.weekend:
        await message.answer(BotMessages.weekend__when.format(when=BotMessages.tomorrow__when))
        return

    msg = generate_study_day(day_of_week_for_tomorrow, timetable_model.date_str, timetable['timetable'])
    await message.answer(BotMessages.college_group.format(college_group) + msg)


async def timetable_for_week__button(message: Message, redis__db_1: RedisStorage, redis__db_2: RedisStorage):
    """
    Отправляет расписание на неделю.
    :param message:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    college_building, college_group, selected_timetable = await get_current_group(
        message.from_user.id, redis__db_1, selected_timetable=True
    )
    new_timetable = await redis__db_2.get_data('timetable_for_new_week')
    key = 'timetable'
    if new_timetable and selected_timetable == 'new_timetable':
        key = 'timetable_for_new_week'
    logging.info(f"User [{message.from_user.id}] | college group [{college_group}] |"
                 f" college building [{college_building}] | timetable [{key}] | расписание [Неделя]")

    timetable_data = await redis__db_2.get_data(key)
    timetable_for_group = timetable_data[college_building][college_group]

    week = ''
    count = 0
    for day_of_week, days in timetable_for_group.items():
        timetable_model = TimetableModel(**days)
        if timetable_model.status != Status.unknown:
            count += 1
            args = (day_of_week, timetable_model.date_str)
            day = generate_study_day(timetable=days['timetable'], *args) if timetable_model.status == Status.study_day \
                else generate_weekend(*args)
            week += day if count == 1 else BotMessages.delimiter + '\n\n' + day

    await message.answer(BotMessages.college_group.format(college_group) + week)

    # Если расписание устарело, то бот сообщит об этом. #
    if not selected_timetable and timetable_is_old(timetable_data['dates']['start_date'], week=True):
        await message.answer(BotMessages.timetable_is_old)


async def timetable_for_days_of_week__section(message: Message, state: FSMContext):
    """
    Подраздел с расписанием по дням недели.
    :param message:
    :param state:
    :return:
    """
    await message.answer(BotMessages.timetable_for_days_of_week, reply_markup=days_of_week_markup())
    await state.set_state(UserTimetableSectionStates.days_of_week)


async def timetable_for_day__input(message: Message, redis__db_1: RedisStorage, redis__db_2: RedisStorage):
    """
    Получает от юзера день недели и отправляет расписание на этот день, если все проверки пройдены.
    :param message:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    college_building, college_group, selected_timetable = await get_current_group(
        message.from_user.id, redis__db_1, selected_timetable=True
    )
    new_timetable = await redis__db_2.get_data('timetable_for_new_week')
    key = 'timetable'
    if new_timetable and selected_timetable == 'new_timetable':
        key = 'timetable_for_new_week'
    logging.info(f"User [{message.from_user.id}] | college group [{college_group}] |"
                 f" college building [{college_building}] | timetable [{key}] | расписание [По дням недели]")

    timetable_data = await redis__db_2.get_data(key)
    timetable_for_group = timetable_data[college_building][college_group]

    day_of_week = message.text
    timetable = timetable_for_group[day_of_week]
    timetable_model = TimetableModel(**timetable)

    # Если расписание устарело, то бот сообщит об этом. #
    if not selected_timetable and timetable_is_old(timetable_data['dates']['start_date'], day=True):
        await message.answer(BotMessages.timetable_is_old)

    # Проверка 1. Если расписания нет. #
    if timetable_model.status == Status.unknown:
        await message.answer(BotErrors.still_no_timetable)
        return

    # Проверка 2. Если выходной. #
    if timetable_model.status == Status.weekend:
        await message.answer(BotMessages.weekend)
        return

    msg = generate_study_day(day_of_week, timetable_model.date_str, timetable['timetable'])
    await message.answer(BotMessages.college_group.format(college_group) + msg)


def timetable_is_old(start_date_str: str, tomorrow=False, week=False, day=False):
    start_date = datetime.datetime(*[int(elem) for elem in start_date_str.split('.')])
    day_of_week = number_to_day_of_week(start_date.weekday())
    days = 5 if day_of_week == 'Среда' else 7
    new_week = start_date + datetime.timedelta(days=days)

    current_date = datetime.datetime.now()
    current_day_of_week = number_to_day_of_week(current_date.weekday())

    # Проверка для расписания на завтра.
    # Если текущий день недели это воскресенье и дата расписания не равна понедельнику следующей недели,
    # то расписание устарело.
    if tomorrow:
        if current_day_of_week == 'Воскресенье' and new_week != start_date:
            return True

    # Проверка для расписания на неделю и по дням недели.
    # Если текущий день недели это пятница или суббота или воскресенье и дата расписания не равна понедельнику
    # следующей недели, то расписание устарело.
    if week or day:
        if current_day_of_week in ['Пятница', 'Суббота', 'Воскресенье'] and new_week != start_date:
            return True


async def timetable_is_new(redis__db_2: RedisStorage):
    """
    Проверяет есть ли в боте новое расписание.
    :param redis__db_2:
    :return:
    """
    timetable_for_new_week = await redis__db_2.get_data('timetable_for_new_week')
    if timetable_for_new_week:
        return True


def month_name_to_number(month_name_raw: str) -> int:
    """
    Получает 'сырую' строку месяца и возвращает номер.
    :param month_name_raw: 'Сырая' строка месяца.
    :return: Номер месяца.
    """
    month_name = month_name_raw.strip().capitalize()
    months = {'Сентября': 9, 'Ноября': 10, 'Октября': 11, 'Декабря': 12, 'Января': 1, 'Февраля': 2, 'Марта': 3,
              'Апреля': 4, 'Мая': 5, 'Июня': 6, 'Июля': 7}
    return months[month_name]


def number_to_day_of_week(number: int) -> str:
    """
    Получает номер дня недели и возвращает строку дня недели.
    :param number: Строка дня недели.
    :return: Строка дня недели.
    """
    week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    return week[number]


def generate_study_day(day_of_week: str, date_str: str, timetable: list) -> str:
    """
    Генерирует строку с расписанием на день.
    :param day_of_week: День недели.
    :param date_str: Строка даты, например: 14 сентября.
    :param timetable: Расписание на этот день.
    :return: Возвращает сгенерированную строку расписания на день.
    """
    return (BotMessages.day_of_week.format(day_of_week=day_of_week, date_str=date_str)
            + ''.join([BotMessages.timetable_for_one_day.format(**item) for item in timetable]))


def generate_weekend(day_of_week: str, date_str: str) -> str:
    """
    Генерирует строку с выходным днем в расписании на неделю.
    :param day_of_week: День недели.
    :param date_str: Строка даты, например: 14 сентября.
    :return: Возвращает сгенерированную строку с выходным днем.
    """
    return (BotMessages.day_of_week.format(day_of_week=day_of_week, date_str=date_str)
            + BotMessages.weekend)


def register_timetable_of_classes(dp: Dispatcher):
    dp.register_message_handler(
        select_timetable,
        text=BotButtons.timetable_of_classes,
        state=MainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=UserTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=UserTimetableSectionStates.select_timetable
    )
    dp.register_message_handler(
        back_to_timetable__button,
        text=BotButtons.back_to_timetable,
        state=UserTimetableSectionStates.days_of_week
    )

    dp.register_message_handler(
        select_timetable__input,
        text=[BotButtons.new_timetable, BotButtons.old_timetable],
        state=UserTimetableSectionStates.select_timetable
    )
    dp.register_message_handler(
        timetable_for_today__button,
        text=BotButtons.timetable_for_today,
        state=UserTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        timetable_for_tomorrow__button,
        text=BotButtons.timetable_for_tomorrow,
        state=UserTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        timetable_for_week__button,
        text=BotButtons.timetable_for_week,
        state=UserTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        timetable_for_days_of_week__section,
        text=BotButtons.timetable_for_day_of_week,
        state=UserTimetableSectionStates.timetable
    )
    dp.register_message_handler(
        timetable_for_day__input,
        text=BotButtons.days_of_week__markup,
        state=UserTimetableSectionStates.days_of_week
    )