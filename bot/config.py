import os
from dataclasses import dataclass

from dotenv import dotenv_values


@dataclass
class VkBot:
    access_token: str
    owner_id: int


@dataclass
class TgBot:
    token: str


@dataclass
class Storages:
    redis_uri__db_1: str
    redis_uri__db_2: str
    postgresql_dsn: str


@dataclass
class Config:
    vkbot: VkBot
    tgbot: TgBot
    storages: Storages
    excel_file: str


def load_config():
    path = os.path.join(os.path.dirname(__file__), ".env")
    config = dotenv_values(path)
    return Config(
        vkbot=VkBot(
            access_token=config.get('ACCESS_TOKEN'),
            owner_id=int(config.get('OWNER_ID'))
        ),
        tgbot=TgBot(
            token=config.get('TOKEN')
        ),
        storages=Storages(
            redis_uri__db_1=config.get('REDIS_URI__DB_1'),
            redis_uri__db_2=config.get('REDIS_URI__DB_2'),
            postgresql_dsn=config.get('PG_DSN')
        ),
        excel_file=config.get('EXCEL_FILE')
    )