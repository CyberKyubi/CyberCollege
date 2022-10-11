import os

from pydantic import BaseSettings, RedisDsn, PostgresDsn


class Config(BaseSettings):
    # Bot #
    token: str

    lucifer_id: int
    doom_id: int

    # Storages #
    redis__db_1: RedisDsn
    redis__db_2: RedisDsn

    postgresql_dsn: PostgresDsn

    # Excel Files #
    excel_file_1: str
    excel_file_2: str
    timetable_changes_1: str
    timetable_changes_2: str

    student_activity: str
    all_logline: str

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        env_file_encoding = 'utf-8'


config = Config()
