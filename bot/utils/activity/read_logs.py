import os
from datetime import datetime, timedelta, date
from calendar import monthrange
from collections import Counter
from typing import List, Dict

import pandas as pd

from config_reader import excel_config, get_project_root
from locales.ru import BotActivity
from utils.activity.enums import PeriodEnum, RoleEnum, StatementEnum
from utils.redis_models.logs import LogLineModel, PointModel, SimpleStudentActivityModel, \
    DetailedStudentActivityModel, TimetableCounterModel


class LogLevels:
    levels = {
        10: 'DEBUG',
        20: 'INFO',
        30: 'WARNING',
        40: 'ERROR',
        50: 'CRITICAL'
    }


class LogMsg:
    timetable_logmsg = {
        'today': '[Сегодня]',
        'tomorrow': '[Завтра]',
        'week': '[Вся неделя]',

        'monday': '[Понедельник]',
        'tuesday': '[Вторник]',
        'wednesday': '[Среда]',
        'thursday': '[Четверг]',
        'friday': '[Пятница]',
        'saturday': '[Суббота]',
    }


def get_files() -> List[List[str]]:
    path = os.path.join(get_project_root(), 'bot/logs/')
    log_files = []
    for _, _, files in os.walk(path):
        log_files.extend(files)
    log_lines = []
    for file in log_files:
        with open(path + file, 'r') as f:
            log_lines.append(f.readlines())
    return log_lines


def get_line_by_level(raw_line: str, level: int):
    loglevel = LogLevels().levels[level]
    try:
        _, levelname, _ = [elem.strip() for elem in raw_line.split('|', maxsplit=2)]
    except ValueError:
        return False
    else:
        if loglevel == levelname:
            return True


def split_logline(raw_line: str):
    without_square_brackets = raw_line[1:-2]
    line = [elem.strip() for elem in without_square_brackets.split('|')]
    asctime = datetime.strptime(line[0], '%d-%m-%Y %H:%M:%S')
    return line, asctime


def new_students(role: str = RoleEnum.user, level: int = 20) -> Dict[str, set]:
    log_lines = get_files()
    logmsg = '[Зарегистрирован]'

    students = {'today': set(), 'week': set(), 'month': set(), 'all_time': set()}
    periods = list(zip(
        ['today', 'week', 'month', 'all_time'],
        [PeriodEnum.today, PeriodEnum.week, PeriodEnum.month, PeriodEnum.all_time]
    ))

    for lines in log_lines:
        for raw_line in lines:
            if get_line_by_level(raw_line, level):
                line, asctime = split_logline(raw_line)
                for key, period in periods:
                    period_result = check_period(asctime.date(), period)
                    if role in line and logmsg in line and period_result:
                        logline_model = line_to_model(line, asctime, line[-1])
                        students[key].add(logline_model.user_id)
    return students


def read_logs(role: str, level: int, period: str, statement, user_id: str = None):
    log_lines = get_files()

    timetable_values = ['[Сегодня]', '[Завтра]', '[Вся неделя]',
                        '[Понедельник]', '[Вторник]', '[Среда]', '[Четверг]', '[Пятница]', '[Суббота]']
    columns = ['asctime', 'levelname', 'name', 'funcName', 'role', 'user_id', 'point', 'message', 'result']

    timetable_logmsg = LogMsg().timetable_logmsg
    all_logline = pd.DataFrame(columns=columns)

    simple_student_activity = SimpleStudentActivityModel()
    detailed_student_activity = DetailedStudentActivityModel()
    timetable_counter = TimetableCounterModel()

    for lines in log_lines:
        for raw_line in lines:
            if get_line_by_level(raw_line, level):
                line, asctime = split_logline(raw_line)
                period_result = check_period(asctime.date(), period)

                if condition(role, line, user_id, period_result, statement):
                    logline_model = line_to_model(line, asctime, line[-1])
                    message = logline_model.message
                    if statement == StatementEnum.one_student:
                        all_logline = pd.concat([all_logline, pd.DataFrame(logline_model.dict(), index=[0])])

                    match logline_model.point:
                        case 'Переход':
                            simple, detailed = simple_student_activity.walking, detailed_student_activity.walking
                            simple_student_activity.walking = count_simple(simple, message)
                            detailed_student_activity.walking = count_detailed(detailed, message)
                        case 'Действие':
                            simple, detailed = simple_student_activity.action, detailed_student_activity.action
                            simple_student_activity.action = count_simple(simple, message)
                            detailed_student_activity.action = count_detailed(detailed, message)
                        case 'Расписание пар':
                            if message not in timetable_values:
                                detailed = detailed_student_activity.timetable
                                detailed_student_activity.timetable = count_detailed(detailed, message)

                            for key, logmsg in timetable_logmsg.items():
                                if logmsg in line:
                                    timetable_counter.timetable[key] += 1
                                    simple_student_activity.timetable.last = logmsg

    simple, timetable_days = generate_msg_simple_activity(simple_student_activity, timetable_counter, period)
    generate_msg_detailed_activity(simple_student_activity, detailed_student_activity, timetable_days)
    if all_logline.empty:
        all_logline.to_excel(excel_config.all_logline)
    return simple


def condition(role: str, line: list, user_id: str, period_result: bool, statement):
    match statement:
        case StatementEnum.one_student:
            if role in line and user_id in line and period_result:
                return True
        case StatementEnum.all_students:
            if role in line and period_result:
                return True


def check_period(asctime: date, period: str):
    if PeriodEnum.all_time == period:
        return True

    now = datetime.now()
    year__int, month__int = now.year, now.month

    if PeriodEnum.today == period and now.date() == asctime:
        return True

    day_of_week = now.date().weekday()
    start__week = now - timedelta(days=day_of_week)
    end__week = start__week + timedelta(days=7)

    if PeriodEnum.week == period and start__week.date() <= asctime < end__week.date():
        return True

    start__month = date(year__int, month__int, 1)
    month_range = monthrange(year__int, month__int)
    end__month = date(year__int, month__int, month_range[1])

    if PeriodEnum.month == period and start__month <= asctime <= end__month:
        return True


def line_to_model(line: list, asctime: datetime, message: str):
    keys = ['asctime', 'levelname', 'name', 'funcName', 'role', 'user_id', 'point', 'message']
    to_dict = dict(zip(keys, line))

    result = ''
    get_result = [elem.strip() for elem in message.split('->')]
    if len(get_result) == 2:
        message, result = get_result

    to_dict.update(asctime=asctime, message=message, result=result)
    return LogLineModel(**to_dict)


def count_simple(point_model: PointModel, message: str) -> PointModel:
    point_model.amount += 1
    point_model.counter[message] += 1
    point_model.last = message
    return point_model


def count_detailed(point: dict, message: str):
    point[message] += 1
    return point


def generate_msg_simple_activity(
        simple_student_activity: SimpleStudentActivityModel,
        timetable_counter: TimetableCounterModel,
        period: str
):
    text = ''
    timetable_days = {}
    student_activity_to_dict = simple_student_activity.dict()
    timetable_counter_to_dict = timetable_counter.dict()

    for point, value in student_activity_to_dict.items():
        amount = value['amount']
        counter = get_most_common(value['counter'])
        last = get_last(value['last'])

        match point:
            case 'walking':
                text += BotActivity.walking % (amount, counter, last)
            case 'action':
                text += BotActivity.action % (amount, counter, last)
            case 'timetable':
                timetable_days = timetable_counter_to_dict['timetable']
                amount = calculate_total_for_timetable(timetable_days)
                text += BotActivity.timetable.format(amount=amount, last=last) + \
                    BotActivity.timetable_days.format(**timetable_days)

    return BotActivity.activity.format(period=period) + text, timetable_days


def generate_msg_detailed_activity(
        simple_student_activity: SimpleStudentActivityModel,
        detailed_student_activity: DetailedStudentActivityModel,
        timetable_days: dict,
):
    detailed_student_activity_to_dict = detailed_student_activity.dict()

    data = {'Пункт': [], 'Сообщения': [], 'Кол-во': []}
    for point, log_messages in detailed_student_activity_to_dict.items():
        points = []
        messages = list(log_messages.keys())
        amount = list(log_messages.values())
        match point:
            case 'walking':
                points = ['Переход']
                total = simple_student_activity.walking.amount
                messages.append(BotActivity.walking_detailed), amount.append(total)
            case 'action':
                points = ['Действие']
                total = simple_student_activity.action.amount
                messages.append(BotActivity.action_detailed), amount.append(total)
            case 'timetable':
                points = ['Расписание пар']
                total = calculate_total_for_timetable(timetable_days) + sum(amount)

                timetable_logmsg = LogMsg().timetable_logmsg
                for key, count in timetable_days.items():
                    messages.append(timetable_logmsg[key]), amount.append(count)

                messages.append(BotActivity.timetable_detailed), amount.append(total)

        points = points * len(messages)

        visual_skip_rows = [None, None]
        points.extend(visual_skip_rows), messages.extend(visual_skip_rows), amount.extend([0, 0])
        data['Пункт'].extend(points), data['Сообщения'].extend(messages), data['Кол-во'].extend(amount)

    df = pd.DataFrame(data)
    df.to_excel(excel_config.student_activity)


def get_most_common(counter: dict):
    counter = Counter(counter)
    if counter:
        return ''.join([msg for msg, count in counter.most_common(1)])
    return 'Нет'


def calculate_total_for_timetable(timetable: dict):
    return sum(list(timetable.values()))


def get_last(msg: str):
    if msg:
        return msg
    return 'Нет'
