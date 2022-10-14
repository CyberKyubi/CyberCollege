import traceback
import asyncio
import datetime
import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup
from keyboards.inline_keyboard_markup import go_to_new_timetable
from states.admin_state_machine import AdminTimetableSectionStates
from handlers.admin.main_menu.menu import admin__main_menu
from utils.timatable.timetable import Timetable
from utils.validation.send_message import send_message
from storages.redis.storage import RedisStorage
from storages.db.requests import insert__college_groups


async def new_timetable__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    logging.info(f"Admin | {message.from_user.id} | Переход | в раздел [Новое расписание]")
    await message.answer(
        BotMessages.send_new_timetable,
        reply_markup=reply_markup('back_to_timetable_section', back=True)
    )
    await state.set_state(AdminTimetableSectionStates.new_timetable)
    await redis__db_1.delete_key('files')


async def preparing(
        files: dict,
        message: Message,
        state: FSMContext,
        session__pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    """
    Добавляет новое расписание.
    :param files: словарь с путями к загруженным файлам.
    :param message:
    :param state:
    :param session__pool:
    :param redis__db_1:
    :param redis__db_2:
    :return:
    """
    obj = NewTimetable(files, message, state, session__pool, redis__db_1, redis__db_2)
    await obj.generate_new_timetable()


class NewTimetable:
    def __init__(
            self,
            files: dict = None,
            message: Message = None,
            state: FSMContext = None,
            session__pool=None,
            redis__db_1: RedisStorage = None,
            redis__db_2: RedisStorage = None,
    ):
        self.files = files

        self.message = message
        self.state = state

        self.session_pool = session__pool
        self.redis__db_1 = redis__db_1
        self.redis__db_2 = redis__db_2

        self.days_of_week = []

    async def generate_new_timetable(self):
        logging.debug(f'BOT | Действие | начало [Новое расписание]')
        college_groups__redis = await self.redis__db_1.get_data('college_groups')
        college_groups__excel = {}

        logging.debug(f'BOT | Действие | новое расписание [Собираю информацию о файлах]')
        # Собирает информацию об расписании. #
        college_buildings = {}
        dates = []
        paths = list(self.files.values())
        for path in paths:
            cls = Timetable(path)
            result = cls.get_groups()
            if not result:
                await self.message.answer(BotErrors.error_in_timetable)
                return
            excel, _ = result

            college_groups__excel.update(excel)

            result = cls.get_info_about_file()
            if not result:
                await self.message.answer(BotErrors.error_in_timetable)
                return
            info, date, self.days_of_week = result

            college_buildings.update(info), dates.append(date)

        # Проверка 1. Если было отправлено два файла для одного корпуса. #
        if len(college_buildings) == 1:
            await self.message.answer(BotErrors.identical_files)
            return

        # Проверка 2. Если разная дата у файлов. #
        date_first_file, date_second_file = dates
        if date_first_file.start != date_second_file.start or date_first_file.end != date_second_file.end:
            await self.message.answer(BotErrors.different_dates)
            return

        # Проверка 3. Если расписание на прошлое. #
        current_week = self.current_week()
        if current_week > date_first_file.start:
            await self.message.answer(BotErrors.old_timetable)
            return

        dates_for_bot = tuple(map(lambda elem: elem[1].strftime('%Y.%m.%d'), date_first_file))
        dates_for_humon = tuple(map(lambda elem: elem[1].strftime('%d.%m.%Y'), date_first_file))

        await self.find_difference(college_groups__redis, college_groups__excel)

        logging.debug(f'BOT | Действие | новое расписание [Добавляю расписание]')
        # Добавляет новое расписание. #
        await self.message.answer(BotMessages.splitting_timetable)
        result = await self.prepare_new_timetable(college_groups__excel, college_buildings, dates_for_bot)
        if result:
            await self.message.answer(BotMessages.timetable_added)
            await admin__main_menu(self.message, self.state)

            users = await self.redis__db_1.get_data('users')
            users_id = users['users_id']

            msg = BotMessages.new_timetable_on.format(*dates_for_humon)
            await asyncio.gather(
                *[send_message(self.message, msg, int(user_id), reply_markup=go_to_new_timetable()) for user_id in users_id]
            )
            logging.info(f"Admin | {self.message.from_user.id} | Действие | добавил [Новое расписание] -> {dates}")
        logging.debug(f'BOT | Действие | конец [Новое расписание]')

    async def find_difference(self, college_groups__redis: dict, college_groups__excel: dict):
        """
        Ищет разницу между сохраненными группами и группами из файла расписания.
        Новые группы добавляет. Удаленные не трогает, так как удаленные, то появляются, то исчезают.
        :param college_groups__redis: Словарь с сохраненными группами.
        :param college_groups__excel: Словарь с группами из расписания.
        Пример словаря: {'Курчатова,16': ['П-419/1', 'П-419/2'], 'Туполева,17а': ['К-190', 'К-191']}
        :return:
        """
        logging.debug(f'BOT | Действие | новое расписание '
                      f'[Ищу разницу между сохраненными группа и группами из расписания]')

        new_groups = {'Курчатова,16': [], 'Туполева,17а': []}
        deleted_groups = []
        for college_building, groups in college_groups__excel.items():
            not_in_redis = list(set(groups) - set(college_groups__redis[college_building]))
            not_in_excel = list(set(college_groups__redis[college_building]) - set(groups))
            if not_in_redis:
                new_groups[college_building].extend(not_in_redis)
            if not_in_excel:
                deleted_groups.extend(not_in_excel)

        new_to_list = new_groups.values()
        new_to_str = 'Нет'
        if any(new_to_list) or deleted_groups:
            deleted_to_str = ', '.join(deleted_groups) if deleted_groups else 'Нет'

            if any(new_to_list):
                new = sum(list(new_groups.values()), [])
                new_to_str = ', '.join(new)
                await self.add_new_groups(new_groups)

            msg = BotMessages.found_difference_between_data.format(new=new_to_str, deleted=deleted_to_str)
            await self.message.answer(msg)
            logging.info(msg)

    async def add_new_groups(self, groups: dict):
        """
        Добавляет новые группы из расписания.
        :param groups: Словарь новых групп. Пример: {'Курчатова,16': ['ПД-121/4', 'ПД-121/5'], 'Туполева,17а': []}
        :return:
        """
        logging.debug(f'BOT | Действие | новое расписание [Добавляю новые группы]')
        college_groups = await self.redis__db_1.get_data('college_groups')
        new = [{'college_building': key, 'college_group': g} for key, value in groups.items() if value for g in value]
        await insert__college_groups(self.session_pool, new)

        [college_groups[key].extend(value) for key, value in groups.items()]
        await self.redis__db_1.set_data('college_groups', college_groups)

    async def prepare_new_timetable(self, college_groups: dict, college_buildings: dict, dates: tuple):
        """
        Записывает в redis новое расписание.
        :param college_groups: словарь с группами.
        :param college_buildings: словарь с информацией о расписании: путь, время расписания.
        :param dates:
        :return:
        """
        old_timetable = await self.redis__db_2.get_data('timetable')

        # Это нужно, чтобы ловить все опечатки в расписании. Например: "Понедельник 10 отября" #
        try:
            new_timetable = await self.splitting_timetable(college_buildings, college_groups)
        except Exception as error:
            logging.error(traceback.format_exc())
            await self.message.answer(BotErrors.error_in_timetable)
        else:
            new_start_date, new_end_date = dates

            if not old_timetable:
                logging.debug(f'BOT | Действие | новое расписание [Записываю расписание в redis] -> ключ [timetable]')
                await self.insert_new_timetable('timetable', new_timetable, new_start_date, new_end_date)
                return True
            else:
                old_start_date, old_end_date = list(map(self.str_to_date, old_timetable['dates'].values()))
                # Проверка 1. Если дата нового расписания равна дате расписанию, которое уже есть. #
                if new_start_date == old_start_date and new_end_date == old_end_date:
                    await self.message.answer(BotErrors.timetable_is_already_there)
                    logging.debug(f'BOT | Ошибка | новое расписание [Расписание с такой же датой уже есть]')
                    return

                # Узнаем на какую неделю расписание. #
                start = self.str_to_date(new_start_date)
                week = start - datetime.timedelta(days=start.weekday())

                current_week = self.current_week()
                current_day_of_week = datetime.datetime.now().weekday()

                # Если расписание на текущую неделю, то обновляет старое расписание. #
                if current_week == week:
                    old_dates = old_timetable.pop('dates')
                    logging.debug(f'BOT | Действие | новое расписание [Обновляю старое расписание]')

                    # Думаю, если еще посидеть, подумать, поискать методы, то можно куда лучше обновить словарь с
                    # расписанием, но пока пусть будет так. #
                    for college_building, timetable in new_timetable.items():
                        update_old_timetable = old_timetable[college_building]
                        result = tuple(map(self.update_old_week, timetable.items(), update_old_timetable.items()))
                        [update_old_timetable.update(timetable_on_group) for timetable_on_group in result]

                    old_dates.update(end_date=new_end_date)
                    old_timetable.update(dates=old_dates)

                    await self.redis__db_2.set_data('timetable', old_timetable)
                    return True

                # Если расписание на следующую неделю, но текущий день недели меньше воскресенья, то сохраняем
                # новое расписание по ключу "timetable_for_new_week", чтобы можно было посмотреть оба расписания.
                elif current_week < week and current_day_of_week < 6:
                    logging.debug(f'BOT | Действие | новое расписание [Записываю расписание в redis] '
                                  f'-> ключ [timetable_for_new_week]')
                    await self.insert_new_timetable('timetable_for_new_week', new_timetable, new_start_date, new_end_date)
                    return True
                else:
                    logging.debug(f'BOT | Действие | новое расписание [Записываю расписание в redis] -> ключ [timetable]')
                    await self.insert_new_timetable('timetable', new_timetable, new_start_date, new_end_date)
                    return True

    @staticmethod
    async def splitting_timetable(college_buildings: dict, college_groups: dict, timetable_changes=False) -> dict:
        """
        Разбивает расписание по группам и собирает в словарь.
        :param college_groups: словарь с группами.
        :param college_buildings: словарь с информацией о расписании: путь, время расписания.
        :param timetable_changes:
        :return:
        """
        logging.debug(f'BOT | Действие | новое расписание [Разбиваю расписание по группам]')
        [college_buildings[key].update(college_groups=college_groups) for key, college_groups in college_groups.items()]

        timetable = {}
        for college_building, values in college_buildings.items():
            cls = Timetable(values['path'], college_building, timetable_changes)
            timetable[college_building] = cls.timetable(values['college_groups'])
        return timetable

    @staticmethod
    def str_to_date(date: str):
        """
        Форматирует строку даты в date type.
        :param date:
        :return:
        """
        date_elem = [int(elem) for elem in date.split('.')]
        return datetime.date(*date_elem)

    @staticmethod
    def current_week() -> datetime.date:
        now = datetime.datetime.now()
        weekday = now.weekday()
        return (now - datetime.timedelta(days=weekday)).date()

    def update_old_week(self, new_timetable: tuple, old_timetable: tuple):
        """
        Обновляет старое расписание, добавляя вторую половину недели.
        :param new_timetable:
        :param old_timetable:
        :return:
        """
        group, new_week = new_timetable
        _, old_week = old_timetable

        days = self.days_of_week
        old_week.update({day_of_week: timetable for day_of_week, timetable in new_week.items() if day_of_week in days})
        return {group: old_week}

    async def insert_new_timetable(self, key: str, new_timetable: dict, start_date, end_date):
        """
        Записывает новое расписание в redis.
        :param key: по которому ключу записать в redis.
        timetable - ключ по умолчанию.
        timetable_for_new_week - расписание на новую неделю.
        :param new_timetable: словарь с новым расписанием.
        :param start_date: строка даты начала расписания.
        :param end_date: строка даты окончания расписания.
        :return:
        """
        new_timetable.update(dates=dict(start_date=start_date, end_date=end_date))
        await self.redis__db_2.set_data(key, new_timetable)


def register_new_timetable(dp: Dispatcher):
    dp.register_message_handler(
        new_timetable__button,
        text=BotButtons.add_timetable,
        state=AdminTimetableSectionStates.timetable
    )
