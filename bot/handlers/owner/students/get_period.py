from locales.ru import BotButtons
from utils.activity.enums import PeriodEnum


def get_period(period: str) -> str:
    match period:
        case BotButtons.activity_today:
            return PeriodEnum.today
        case BotButtons.activity_week:
            return PeriodEnum.week
        case BotButtons.activity_month:
            return PeriodEnum.month
        case _:
            return PeriodEnum.all_time