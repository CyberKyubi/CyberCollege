import os
from dataclasses import dataclass
from typing import List

from dotenv import dotenv_values


@dataclass
class TgBot:
    token: str
    admins_id: List[int]
    owners_id: List[int]
    lucifer: int


@dataclass
class Storages:
    redis_uri__db_1: str
    redis_uri__db_2: str
    postgresql_dsn: str


@dataclass
class Config:
    tgbot: TgBot
    storages: Storages
    excel_file_1: str
    excel_file_2: str


def load_config():
    path = os.path.join(os.path.dirname(__file__), ".env")
    config = dotenv_values(path)
    return Config(
        tgbot=TgBot(
            token=config.get('TOKEN'),
            admins_id=[int(admin_id) for admin_id in config.get('ADMINS_ID').split(',')],
            owners_id=[int(admin_id) for admin_id in config.get('OWNERS_ID').split(',')],
            lucifer=int(config.get('LUCIFER'))
        ),
        storages=Storages(
            redis_uri__db_1=config.get('REDIS_URI__DB_1'),
            redis_uri__db_2=config.get('REDIS_URI__DB_2'),
            postgresql_dsn=config.get('PG_DSN')
        ),
        excel_file_1=config.get('EXCEL_FILE_1'),
        excel_file_2=config.get('EXCEL_FILE_2')
    )