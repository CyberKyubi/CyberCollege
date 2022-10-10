import datetime
from collections import Counter
from typing import Dict

from pydantic import BaseModel


class LogLineModel(BaseModel):
    asctime: datetime.datetime
    levelname: str
    name: str
    funcName: str
    role: str
    user_id: str
    point: str
    message: str
    result: str


class PointModel(BaseModel):
    amount: int = 0
    counter: Counter = Counter()
    last: str = ''


class SimpleStudentActivityModel(BaseModel):
    walking: PointModel = PointModel()
    action: PointModel = PointModel()
    timetable: PointModel = PointModel()


class DetailedStudentActivityModel(BaseModel):
    walking = {
        'раздел [Регистрация]': 0,
        '[Впервые зашел в бота]': 0,
        'раздел [Главное меню]': 0,
        'раздел [Удалить аккаунт]': 0,
        'раздел [Отправить feedback]': 0,
        'раздел [Написать feedback]': 0,
        'раздел [Настройки]': 0,
        'раздел [Расписание пар]': 0,
        'раздел [По дням недели]': 0,
        'раздел [Группы друзей]': 0,
        'раздел [Выбор группы]': 0,
        'раздел [Редактировать группы]': 0,
        'раздел [Добавить группу]': 0,
        'раздел [Удалить группу]': 0
    }

    action = {
        '[Зарегистрирован]': 0,
        '[Показать расписание перемен]': 0,
        '[Удалить аккаунт] > Ответ [Нет]': 0,
        '[Удалить аккаунт] > Ответ [Да]': 0,
        '[Удален из бота]': 0,
        '[Отправил сообщение]': 0,
        '[Получил мой сервисный аккаунт тг.]': 0,
        '[Будет добавлять первую группу друга]': 0,
        '[Будет добавлять группу друга]': 0,
        '[Выбрал группу]': 0,
        '[Добавил группу друга]': 0,
        '[Вернулся на свою группу]': 0,
        '[Будет переходить на группу друга]': 0,
        '[Перешел на группу]': 0,
        '[Будет удалять группу]': 0,
        '[Удалил группу]': 0,
        '[Получил секрет]': 0
    }

    timetable = {
        'Предложен выбор расписания [Старое/Новое]': 0,
        '[Выбор расписания] > Ответ [Старое расписание]': 0,
        '[Выбор расписания] > Ответ [Новое расписание]': 0,
        '[Кликнул по кнопке нового расписания в уведомлении]': 0
    }


class TimetableCounterModel(BaseModel):
    timetable: Dict[str, int] = {
        'today': 0,
        'tomorrow': 0,
        'week': 0,

        'monday': 0,
        'tuesday': 0,
        'wednesday': 0,
        'thursday': 0,
        'friday': 0,
        'saturday': 0,
    }