import re
import datetime
import logging
import traceback
from typing import Optional, Tuple

import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np

from utils.redis_models.timetable import DatesModel


class Timetable:
    """
    Класс для чтения файлов с расписанием.
    """

    def __init__(self, excel_file: str, default_college_building: Optional[str] = None, timetable_changes=False):
        self.excel_file = excel_file

        self.default_college_building = default_college_building
        self.college_building_1 = 'Курчатова,16'
        self.college_building_2 = 'Туполева,17а'

        self.timetable_changes: bool = timetable_changes

        self.dates = []
        self.days_of_week = []

        self.previous_number = 0
        self.times = ['8.00-9.10', '9.20-10.30', '10.50-12.00', '12.10-13.20', '13.30-14.40', '15.00-16.10',
                      '16.20-17.30', '17.40-18.50']
        self.index_of_time = 0

    def timetable(self, college_groups: list):
        """
        Записывает расписание каждой группы в словарь.
        :param college_groups:
        :return:
        """
        timetable = {group: self.prepare_timetable(group) for group in college_groups}
        return timetable

    def data_integrity_check(self, df: DataFrame):
        """
        Проверка целостности данных. Защита от большинства проблем в расписании.
        :param df:
        :return:
        """
        df.rename(columns={'Unnamed: 0': 'Date', 'Unnamed: 1': 'Number', 'время': 'Time'}, inplace=True)
        df = df.drop(df.tail(1).index)

        column__date_str = (df['Date']
                            .dropna()
                            .apply(self.check_date_str)
                            )
        df.update(column__date_str)

        column__number = (df['Number']
                          .replace(np.nan, 0)
                          .astype(np.int8)
                          .apply(self.check_number)

        )
        column__time = (df['Time']
                        .replace(np.nan, 0)
                        .apply(self.check_time)
                        )
        cleared_df = pd.merge(column__number, column__time, right_index=True, left_index=True)
        df.update(cleared_df)
        df['Number'] = df['Number'].astype(np.int8)
        return df

    def check_date_str(self, date_str: str) -> str:
        """
        Проверяет строку даты. Каждый элемент строки проверяется по отдельности.
        :param date_str: Пример строки: "Понедельник 10 октября".
        :return:
        """
        string = date_str.strip()
        elems_string = string.split()
        if len(elems_string) == 3:
            day_of_week, day, month = elems_string
        else:
            day_of_week, day, month = self.check_day(elems_string)

        day_of_week = self.check_day_of_week(day_of_week.title())
        month = self.check_month(month.lower())
        return '%s %s %s' % (day_of_week, day, month)

    @staticmethod
    def check_day_of_week(day_of_week: str) -> str:
        """
        Проверяется день недели. Если дня недели нет в списке, то забирается
        по аббревиатуре(первые две буквы) день недели.
        :param day_of_week: Пример дня недели: 'Понедельник'.
        :return:
        """
        week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        days_abbr = ['По', 'Вт', 'Ср', 'Че', 'Пя', 'Су']
        if day_of_week not in week:
            day_abbr = day_of_week[:2]
            day_of_week = week[days_abbr.index(day_abbr)]
        return day_of_week

    @staticmethod
    def check_day(elems_string: list) -> Tuple[str, str, str]:
        """
        Проверяется день. Если кол-во элементов строки 2, то находим день в конце первого элемента,
        или в начале второго элемента. Если кол-во элементов строки 1, то находим число в строке и разбиваем ее.
        :param elems_string:
        :return:
        """
        if len(elems_string) == 2:
            day_of_week, month = elems_string
            endswith, startswith = day_of_week[-2:], month[:2]
            if endswith.isdigit():
                day_of_week = day_of_week.replace(endswith, '')
                return day_of_week, endswith, month
            if startswith.isdigit():
                month = month.replace(startswith, '')
                return day_of_week, startswith, month

        elif len(elems_string) == 1:
            day = re.search(r'\d{1,2}', elems_string[0]).group()
            day_of_week, month = elems_string[0].split(day)
            return day_of_week, day, month

    @staticmethod
    def check_month(month: str) -> str:
        """
        Проверяется месяц. Находит аббревиатуру месяца и по ней забирается месяц из словаря.
        :param month:
        :return:
        """
        month_name = {'сен': 'сентября', 'окт': 'октября', 'нояб': 'ноября', 'дек': 'декабря', 'янв': 'января',
                      'фев': 'февраля', 'мар': 'марта', 'апр': 'апреля', 'мая': 'мая', 'июн': 'июня', 'июл': 'июля'}
        month_attr = re.search(r'(сен|окт|нояб|дек|янв|фев|мар|апр|мая|июн|июл)', month).group()
        return month_name[month_attr]

    def check_number(self, number: int):
        """
        Проверяет номер пары. Если он пропущен, то записывает предыдущий номер + 1.
        :param number:
        :return:
        """
        if number == 0 and self.previous_number != 8:
            self.previous_number += 1
            return self.previous_number
        else:
            self.previous_number = number
            return number

    def check_time(self, time: str):
        """
        Проверяет время пар. Опирается на первые два времени(уж они то должны быть обязательно в файлах).
        Если временя пропущено, то забирается по индексу время из списка всех времен.
        :param time:
        :return:
        """
        if time == self.times[0] or self.index_of_time == 8:
            self.index_of_time = 0

        match time:
            case 'время':
                return time
            case 0:
                time = self.times[self.index_of_time]
                if self.index_of_time != 7:
                    self.index_of_time += 1
                return time
            case _:
                if self.times[self.index_of_time] != time:
                    time = self.times[self.index_of_time]
                self.index_of_time += 1
                return time

    def prepare_timetable(self, group: str):
        """
        Подготавливает расписания для указанной группы.
        :param group:
        :return:
        """
        # Строки плавают от расписания к расписанию. Поэтому нужно индекс строки 'время',
        # чтобы проскипать до этой строки. #
        df_for_get_index = pd.read_excel(self.excel_file, sheet_name=0)
        skiprows = df_for_get_index.index[df_for_get_index['Unnamed: 2'] == 'время'].tolist()[0] + 1

        df = pd.read_excel(self.excel_file, sheet_name=0, skiprows=skiprows)
        df = self.data_integrity_check(df)

        # Криворукость не знает границ. #
        try:
            raw_timetable = df[['Date', 'Number', 'Time', group]].copy()
        except KeyError as error:
            logging.error(error)
            return

        study_days_df = (raw_timetable
                         .replace(1, np.nan)
                         .drop(index=df.index[df['Time'] == 'время'].to_list())
                         .dropna(how='all')
                         .pipe(self.fillna_in_dates)
                         .pipe(self.drop_weekends, group=group)
                         .dropna(subset=[group])
                         )

        all_dates = self.get_dates(raw_timetable)
        study_days = self.get_dates(study_days_df)
        weekends = [date.split(' ', maxsplit=1) for date in all_dates if date not in study_days]

        # В случае изменений в расписании. Если учебный день изменили на выходной|ые, то df будет пустым. #
        if not study_days_df.empty:
            study_days_df[['DayOfWeek', 'DateString']] = (study_days_df['Date'].str.split(n=1, expand=True))
            study_days_df.drop('Date', axis=1, inplace=True)

            study_days_df[['Teacher', 'Subject', 'Cabinet', 'College building']] = (
                study_days_df[group].apply(self.split_info).str.split(';', expand=True)
            )
            study_days_df.drop(group, axis=1, inplace=True)

        timetable = self.parse_dataframe(study_days_df, weekends)
        return timetable

    @staticmethod
    def get_dates(df) -> list[str]:
        """
        Забирает дату из колоны.
        :param df:
        :return:
        """
        return [date for date in df['Date'] if isinstance(date, str)]

    def fillna_in_dates(self, df) -> DataFrame:
        """
        Заполняет пустые поля датой.
        :param df:
        :return:
        """
        indexes = df.index[df['Number'] == 2].to_list()
        all_dates = self.get_dates(df)
        for index, date in zip(indexes, all_dates):
            df.loc[index:index + 6, 'Date'] = date
        return df

    @staticmethod
    def drop_weekends(df: DataFrame, group: str) -> DataFrame:
        """
        Удаляет из расписания 'День самоподготовки', чтобы поле было пустым, тем самым помечается как выходной.
        :param df:
        :param group:
        :return:
        """
        df[group] = df.apply(
            lambda x: x[group].strip() if isinstance(x[group], str) else x[group], axis=1
        )
        df.replace('День самоподготовки', None, inplace=True)
        return df

    def split_info(self, info: str) -> str:
        """
        Парсинг строки с информацией о паре.
        Разбивается на: кабинет, корпус, преподаватель, дисциплина.
        :param info: Пример: "МДК 11.01 Коннова Г.П. Каб.7 (Туполева,17а)".
        :return:
        """
        cabinet = re.search(r'[К-к]аб.\s?\d{1,2}', info)
        if cabinet:
            cabinet = cabinet.group()
        else:
            cabinet_without_number = re.search(r'[К-к]аб.\s?', info)
            if cabinet_without_number:
                info = info.replace(cabinet_without_number.group(), '')
                cabinet = 'Каб.666 (Потерян)'
            else:
                cabinet = 'Улица или спортзал'

        prepared_college_building = re.search(r'(?<=\().*(?=\))', info)
        if prepared_college_building:
            college_building = prepared_college_building.group()
            info = info.replace(f'({college_building})', '')
        else:
            college_building = self.default_college_building

        teacher = re.search(r'\w+[А-я]\s[А-Я].[А-Я].', info)
        if teacher:
            teacher = teacher.group()
        else:
            teacher = 'Нет препода'

        for elem_to_replace in [cabinet, teacher]:
            info = info.replace(elem_to_replace, '')
        subject = info.strip()
        return ';'.join([teacher, subject, cabinet, college_building])

    def parse_dataframe(self, df: DataFrame, weekends: list):
        """
        Собирается расписание по дням недели в словарь.
        :param df:
        :param weekends:
        :return:
        """
        keys = ['number', 'time', 'day_of_week', 'date_str', 'teacher', 'subject', 'cabinet', 'college_building']
        timetable = {
            'Понедельник': {'timetable': [], 'date_str': '', 'status': 'unknown', 'msg': ''},
            'Вторник': {'timetable': [], 'date_str': '', 'status': 'unknown', 'msg': ''},
            'Среда': {'timetable': [], 'date_str': '', 'status': 'unknown', 'msg': ''},
            'Четверг': {'timetable': [], 'date_str': '', 'status': 'unknown', 'msg': ''},
            'Пятница': {'timetable': [], 'date_str': '', 'status': 'unknown', 'msg': ''},
            'Суббота': {'timetable': [], 'date_str': '', 'status': 'unknown', 'msg': ''}
        }

        raw_timetables = [dict(zip(keys, row)) for row in df.values]
        for raw_timetable in raw_timetables:
            current_day = timetable[raw_timetable['day_of_week']]
            current_day.update(date_str=raw_timetable.pop('date_str').strip(), status='study_day')
            current_day['timetable'].append(raw_timetable)

        if weekends:
            msg, status = 'Выходной', 'weekend'
            [timetable[day_of_week].update(date_str=date_str, msg=msg, status=status)
             for day_of_week, date_str in weekends]

        if self.timetable_changes:
            timetable_changes = {}
            for key, value in timetable.items():
                if value['status'] != 'unknown':
                    timetable_changes.update({key: value})
            return timetable_changes
        return timetable

    def get_info_about_file(self) -> tuple[dict, DatesModel, list] | None:
        """
        Забираем из файла расписания информацию: путь к файлу, время расписания.
        :return: При успехе возвращает информацию.
        """
        try:
            raw_df, _ = self.dates_of_timetable()

            college_building = self.get_college_building(raw_df)
        except Exception as error:
            logging.error(traceback.format_exc())
        else:
            return \
                {college_building: {'path': self.excel_file}}, \
                DatesModel(start=self.dates[0], end=self.dates[-1]), \
                self.days_of_week
        return

    def dates_of_timetable(self) -> Tuple[DataFrame, list]:
        raw_df = pd.read_excel(self.excel_file, sheet_name=0)

        skiprows = raw_df.index[raw_df['Unnamed: 2'] == 'время'].tolist()[0] + 1
        df = pd.read_excel(self.excel_file, sheet_name=0, skiprows=skiprows)

        df = self.data_integrity_check(df)
        (df['Date']
         .dropna()
         .apply(self.date_parse)
         )
        return raw_df, self.dates

    def date_parse(self, raw_date: str):
        """
        Собирается дата. Из строки даты забирается день и строка месяца.
        Год - текущий.
        Месяц - из строки месяца получаем номер месяца.
        :param raw_date: Пример: "Понедельник 12 сентября".
        :return:
        """
        date_elems = raw_date.split()
        self.days_of_week.append(date_elems[0])

        day = int(re.search(r'\d{1,2}', raw_date).group())
        month_number = {'сен': 9, 'окт': 10, 'нояб': 11, 'дек': 12, 'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5,
                        'июн': 6, 'июл': 7}
        month = re.search(r'(сен|окт|нояб|дек|янв|фев|мар|апр|мая|июн|июл)', raw_date.lower()).group()
        month = month_number[month]
        date = datetime.date(year=datetime.datetime.now().year, month=month, day=day)
        self.dates.append(date)

    @staticmethod
    def get_college_building(df: DataFrame):
        """
        Ищет в расписании корпус и возвращает его.
        :param df:
        :return:
        """
        mask = np.column_stack([df[col].astype(str).str.contains('Расписание занятий на', na=False) for col in df])
        row: DataFrame = df.loc[mask.any(axis=1)]
        row = row.dropna(axis=1)
        result = [string for elems in row.values for string in elems if 'Расписание занятий на' in string]
        college_building = re.search(r'(Курчатова,\s?\d{2}|Туполева,\s?\d{2}а)', result[0]).group()
        college_building = ''.join(college_building.split())
        return college_building

    def get_groups(self) -> Tuple[dict, list] | None:
        """
        Собирает все группы из расписания.
        :return: При успехе возвращает группы.
        """
        try:
            df_for_get_index = pd.read_excel(self.excel_file, sheet_name=0)
            skiprows = df_for_get_index.index[df_for_get_index['Unnamed: 2'] == 'время'].tolist()[0] + 1

            df = pd.read_excel(self.excel_file, sheet_name=0, skiprows=skiprows)
            college_building = self.default_college_building
            if not college_building:
                college_building = self.get_college_building(df_for_get_index)
            groups = df.columns.tolist()[3:]

            redis = {college_building: groups}
            db = [{'college_group': group, 'college_building': college_building} for group in groups]
        except Exception as error:
            logging.error(traceback.format_exc())
        else:
            return redis, db
        return
