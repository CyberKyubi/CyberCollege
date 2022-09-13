import re

import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np


class Timetable:
    def __init__(self, excel_file: str, group: str):
        self.excel_file = excel_file
        self.group = group

        self.college_building_1 = 'Курчатова,16'
        self.college_building_2 = 'Туполева,17а'

    def prepare_dataframe(self):
        df = pd.read_excel(self.excel_file, sheet_name=0, skiprows=10)

        raw_timetable = df[['Unnamed: 0', 'Unnamed: 1', 'время', self.group]].copy()
        raw_timetable.rename(columns={'Unnamed: 0': 'Date', 'Unnamed: 1': 'Number', 'время': 'Time'}, inplace=True)

        study_days_df = (raw_timetable
                         .drop(index=raw_timetable.index[raw_timetable['Time'] == 'время'].to_list())
                         .dropna(how='all')
                         .pipe(self.fillna_in_dates)
                         .dropna(subset=[self.group])
                         )

        all_dates = self.get_dates(raw_timetable)
        study_days = self.get_dates(study_days_df)
        weekends = [date.split(' ', maxsplit=1) for date in all_dates if date not in study_days]

        study_days_df[['DayOfWeek', 'DateString']] = study_days_df['Date'].str.split(n=1, expand=True)
        study_days_df.drop('Date', axis=1, inplace=True)

        study_days_df[['Teacher', 'Subject', 'Cabinet', 'College building']] = (
            study_days_df[self.group].apply(self.split_info).str.split(';', expand=True)
        )
        study_days_df.drop(self.group, axis=1, inplace=True)

        # study_days_df.to_excel('/home/wither/PycharmProjects/college_timetable/bot/excel_file/our_timetable.xlsx')
        timetable = self.parse_dataframe(study_days_df, weekends)
        return timetable

    @staticmethod
    def get_dates(df) -> list[str]:
        return [date for date in df['Date'] if isinstance(date, str)]

    def fillna_in_dates(self, df) -> DataFrame:
        df['Number'] = df['Number'].astype(np.int8)
        indexes = df.index[df['Number'] == 2].to_list()
        all_dates = self.get_dates(df)
        for index, date in zip(indexes, all_dates):
            df.loc[index:index + 6, 'Date'] = date
        return df

    def split_info(self, info: str) -> str:
        cabinet = re.search(r'Каб.\d{1,2}', info).group()

        prepared_college_building = "(%s)" % (self.college_building_2, )
        if prepared_college_building not in info:
            college_building = self.college_building_1
        else:
            college_building = self.college_building_2

        teacher = re.search(r'\w+[А-я]\s[А-Я].[А-Я].', info).group()

        for elem_to_replace in [cabinet, prepared_college_building, teacher]:
            info = info.replace(elem_to_replace, '')
        subject = info.strip()
        return ';'.join([teacher, subject, cabinet, college_building])

    @staticmethod
    def parse_dataframe(df: DataFrame, weekends: list):
        keys = ['number', 'time', 'day_of_week', 'date_str', 'teacher', 'subject', 'cabinet', 'college_building']
        timetable = {'Понедельник': [], 'Вторник': [], 'Среда': [], 'Четверг': [], 'Пятница': [], 'Суббота': []}
        [timetable[row[2]].append(dict(zip(keys, row))) for row in df.values]

        if weekends:
            timetable.update({day_of_week: dict(date_str=date_str, msg='Выходной') for day_of_week, date_str in weekends})
        return timetable


# a = Timetable("/home/wither/PycharmProjects/college_timetable/bot/excel_file/timetable.xls", 'П-419/2')
# a.prepare_dataframe()