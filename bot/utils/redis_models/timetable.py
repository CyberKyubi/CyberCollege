from enum import Enum

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
