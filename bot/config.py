import os
from dataclasses import dataclass

from dotenv import dotenv_values


@dataclass
class TgBot:
    token: str
    lucifer: int
    doom: int


@dataclass
class Storages:
    redis_uri__db_1: str
    redis_uri__db_2: str
    postgresql_dsn: str


@dataclass
class UserActivity:
    student: str
    all_logline: str


@dataclass
class Config:
    tgbot: TgBot
    storages: Storages
    user_activity: UserActivity
    excel_file_1: str
    excel_file_2: str
    timetable_changes_1: str
    timetable_changes_2: str


def load_config():
    path = os.path.join(os.path.dirname(__file__), ".env")
    config = dotenv_values(path)
    return Config(
        tgbot=TgBot(
            token=config.get('TOKEN'),
            lucifer=int(config.get('LUCIFER')),
            doom=int(config.get('DOOM'))
        ),
        storages=Storages(
            redis_uri__db_1=config.get('REDIS_URI__DB_1'),
            redis_uri__db_2=config.get('REDIS_URI__DB_2'),
            postgresql_dsn=config.get('PG_DSN')
        ),
        user_activity=UserActivity(
            student=config.get('STUDENT_ACTIVITY'),
            all_logline=config.get('ALL_LOGLINE')
        ),
        excel_file_1=config.get('EXCEL_FILE_1'),
        excel_file_2=config.get('EXCEL_FILE_2'),
        timetable_changes_1=config.get('TIMETABLE_CHANGES_1'),
        timetable_changes_2=config.get('TIMETABLE_CHANGES_2'),
    )