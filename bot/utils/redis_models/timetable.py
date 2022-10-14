from enum import Enum
from datetime import date

from pydantic import BaseModel


class Status(str, Enum):
    study_day = 'study_day'
    unknown = 'unknown'
    weekend = 'weekend'


class TimetableModel(BaseModel):
    date_str: str
    status: Status
    msg: str

    class Config:
        use_enum_values = True


class DatesModel(BaseModel):
    start: date
    end: date
