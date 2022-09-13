class BotMessages:
    user__main_menu = 'Ты в главном меню'

    select_college_group = 'Так как ты новенький, то выбери группу:'

    today__when = 'Сегодня'
    tomorrow__when = 'Завтра'
    week__when = 'Выходной'
    weekend__when = '{when} выходной!'

    college_group = '{}\n'
    day_of_week = '{day_of_week} - {date_str}\n\n'
    timetable_for_one_day = '{number} пара {time}\n' \
                            '{subject}\n' \
                            '{teacher} / {cabinet} ({college_building})\n\n'
    weekend = 'Выходной'


class BotButtons:
    group_1 = 'П-419/1'
    group_2 = 'П-419/2'
    groups__markup = [group_1, group_2]

    timetable_for_today = 'Расписание на сегодня'
    timetable_for_tomorrow = 'Расписание на завтра'
    timetable_for_week = 'Расписание на неделю'
    timetable__markup = [timetable_for_today, timetable_for_tomorrow, timetable_for_week]

    reply_markup = {
        'groups': groups__markup,
        'timetable': timetable__markup
    }


class BotErrors:
    day_of_week_is_sunday = '{when} воскресенье :)'
    timetable_not_found = 'Расписания еще нет..'
