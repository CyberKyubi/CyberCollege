import os
from pathlib import Path

from pydantic import BaseSettings, BaseModel, RedisDsn, PostgresDsn, validator


def get_project_root() -> Path:
    return Path(__file__).parent.parent


class Config(BaseSettings):
    # Bot #
    token: str

    lucifer_id: int
    doom_id: int

    # Storages #
    redis__db_1: RedisDsn
    redis__db_2: RedisDsn

    postgresql_dsn: PostgresDsn

    class Config:
        env_file = os.path.join(get_project_root(), ".env")
        env_file_encoding = 'utf-8'


class ExcelConfig(BaseModel):
    # Расписание #
    timetable_1: str = 'timetable_1.xls'
    timetable_2: str = 'timetable_2.xls'
    timetable_changes_1: str = 'timetable_changes_1.xls'
    timetable_changes_2: str = 'timetable_changes_2.xls'

    # Активность #
    student_activity: str = 'detailed_student_activity.xlsx'
    all_logline: str = 'all_logline.xlsx'

    @validator('*', always=True)
    def validate_date(cls, value, values, config, field):
        return os.path.join(get_project_root(), 'bot/excel_file',  value)


app_config = Config()
excel_config = ExcelConfig()

