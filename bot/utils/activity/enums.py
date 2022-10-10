from enum import Enum


class StatementEnum(str, Enum):
    one_student = 'one'
    all_students = 'all'


class RoleEnum(str, Enum):
    user = 'User'
    admin = 'Admin'
    owner = 'Owner'


class PeriodEnum(str, Enum):
    today = 'Today'
    week = 'Week'
    month = 'Month'
    all_time = 'All time'


class LogLevelEnum(int, Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
