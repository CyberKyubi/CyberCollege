import re
import datetime
import logging
from typing import Optional, Tuple

import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np


class Timetable:
    """
    Класс для обработки расписания.
    """
    def __init__(self, excel_file: str, default_college_building: Optional[str] = None):
        self.excel_file = excel_file

        self.default_college_building = default_college_building
        self.college_building_1 = 'Курчатова,16'
        self.college_building_2 = 'Туполева,17а'

        self.dates = []

    def timetable(self, college_groups: list):
        timetable = {group: self.prepare_timetable(group) for group in college_groups}
        return timetable

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

        # Криворукость не знает границ. #
        try:
            raw_timetable = df[['Unnamed: 0', 'Unnamed: 1', 'время', group]].copy()
        except KeyError as error:
            logging.error(error)
            return
        raw_timetable.rename(columns={'Unnamed: 0': 'Date', 'Unnamed: 1': 'Number', 'время': 'Time'}, inplace=True)

        study_days_df = (raw_timetable
                         .drop(raw_timetable.tail(1).index)
                         .drop(index=raw_timetable.index[raw_timetable['Time'] == 'время'].to_list())
                         .dropna(how='all')
                         .pipe(self.fillna_in_dates)
                         .pipe(self.drop_weekends, group=group)
                         .dropna(subset=[group])
                         )

        all_dates = self.get_dates(raw_timetable)
        study_days = self.get_dates(study_days_df)
        weekends = [date.split(' ', maxsplit=1) for date in all_dates if date not in study_days]

        study_days_df[['DayOfWeek', 'DateString']] = study_days_df['Date'].str.split(n=1, expand=True)
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
        df['Number'] = df['Number'].astype(np.int8)
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

    @staticmethod
    def parse_dataframe(df: DataFrame, weekends: list):
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
        return timetable

    def get_info_about_file(self) -> tuple[dict, dict]:
        """
        Забираем из файла расписания информацию: путь к файлу, время расписания.
        :return:
        """
        df = pd.read_excel(self.excel_file, sheet_name=0)
        date = pd.read_excel(self.excel_file, sheet_name=0, skiprows=9)
        (date['Unnamed: 0']
         .dropna()
         .apply(self.date_parse)
        )

        college_building = self.get_college_building(df)
        return {college_building: {'path': self.excel_file}}, {'start_date': self.dates[0], 'end_date': self.dates[-1]}

    def date_parse(self, raw_date: str):
        """
        Собирается дата. Из строки даты забирается день и строка месяца.
        Год - текущий.
        Месяц - из строки месяца получаем номер месяца.
        :param raw_date: Пример: "12 Сентября".
        :return:
        """
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
        college_building = result[0].replace('Расписание занятий на', '').strip()
        return college_building

    def get_groups(self) -> Tuple[dict, list]:
        """
        Собирает все группы из расписания.
        :return:
        """
        df_for_get_index = pd.read_excel(self.excel_file, sheet_name=0)
        skiprows = df_for_get_index.index[df_for_get_index['Unnamed: 2'] == 'время'].tolist()[0] + 1

        df = pd.read_excel(self.excel_file, sheet_name=0, skiprows=skiprows)
        college_building = self.get_college_building(df_for_get_index)
        groups = df.columns.tolist()[3:]

        redis = {college_building: groups}
        db = [{'college_group': group, 'college_building': college_building} for group in groups]
        return redis, db
