class BotMessages:
    """
    Класс со всеми сообщениями бота.
    """
    # Создатель #
    # Главное меню и разделы #
    owner__main_menu = 'Рад тебя снова видеть, Люцик!'
    change_role__section = '^👨🏼‍🎓^  RoLes  ^🧙🏼‍♂^'
    owner__section = '🧛🏻 Owners:\n\n'
    deploy__section = '🛠 Execute functions in order:'

    # Owners Section #
    owner = '{number}) {mention}\n' \
            '<i><code>{user_id}</code></i>\n'

    add_owner = '➕🧛🏻 Add owner\n' \
                'Напиши <i><code>user_id</code></i>:'
    delete_owner = '➖🧛🏻 Delete owner\n' \
                   'Напиши <i><code>user_id</code></i>:'
    owner_added = 'Owned added!'
    owner_deleted = 'Owner deleted'
    you_have_been_added_to_owner_role = 'Ты добавлен в роль: 🧛🏻 Owner'
    you_have_been_delete_from_owner_role = 'Тебя удалили из роли: 🧛🏻 Owner\n' \
                                           'Вызови команду /start, чтобы перейти в меню студента'

    # Deploy #
    confirm_your_action = 'Подтверди свое действие:\n' \
                          '{action}'
    truncate_storages__action = 'Ты действительно хочешь очистить хранилища?'
    storages_cleared = 'Хранилища очищены!'

    excel_files = 'Отправь два файла с расписанием по одному:'
    received_documents = 'Получил документы'
    groups = 'Группы:\n'
    received_groups = '{building}\n' \
                      '{groups}\n\n'
    redis_is_ready = 'Redis заполнен'

    message_from = 'Сообщение от студента:\n' \
                   'user_id: {}\n' \
                   'Группа: {}\n' \
                   'Корпус: {}'

    # Админ #
    admin__main_menu = 'Рад Вас видеть, администрация!\n' \
                       'Вы находитесь 🏠 Главном меню'
    admin_timetable__section = 'Вы перешли в раздел для работы с 📖 расписанием'

    send_new_timetable = 'Отправляйте расписание по одному файлу:'
    splitting_timetable = 'Разбиваю расписание по группам...'
    found_difference_between_data = 'Нашел разницу между сохраненными группа и группами из расписания:\n' \
                                    'В сохраненных группах нет: {new}\n' \
                                    'В расписании нет: {deleted}'
    timetable_added = 'Новое расписание добавлено!'

    timetable_changes_in = 'Изменения в расписании у:'
    choose_college_building = 'Кликните по кнопке корпуса, у которого изменения в расписании:'
    choose_first_college_building = 'Чтобы внести изменения у двух корпусов, нужно сначала выбрать первый корпус.\n\n' \
                                    'Кликните по кнопке корпуса: '
    send_timetable_changes = 'Отправьте файл c расписанием:'
    send_first_timetable_changes = 'Отправьте первый файл с изменениями:'
    send_second_timetable_changes = 'Теперь второй файл:'

    timetable_changes_saved = 'Изменения в расписании сохранены!'
    timetable_changes_not_saved = 'Изменения в расписании не сохранены!\n\n' \
                                  'Возможно, Вы кликнули по одному корпусу, а отправили файл с расписанием на ' \
                                  'другой корпус.\n' \
                                  'Или эти изменения уже есть.'
    # Юзер (студент) #
    # Регистрация. #
    registration = 'Привет, 👨🏼‍🎓 студент, вижу, что ты еще не зарегистрирован в боте!\n' \
                   'А это значит, что тебе нужно ' \
                   'написать свою группу, чтобы получать 📖 расписание.\n' \
                   'Пример группы: П-419/2\n\n' \
                   'Сейчас ты напишешь свою 📚 группу, \nа после в ⚙️ настройках, ты можешь добавить еще 📚 группы, ' \
                   'чтобы 👀 смотреть расписание своих друзей!' \

    # Главное меню и разделы. #
    user__main_menu = '📚 {college_group}\n\n' \
                      'Рад тебя видеть, 👨🏼‍🎓 студент!\n' \
                      'Ты находишься в 🏠 Главном меню'

    user_timetable__section = 'Смотрим расписание 👀'

    settings__section = 'В этом разделе ты можешь:\n' \
                        '▫️ Добавлять группы своих друзей, чтобы посмотреть их расписание\n' \
                        '▫️ Написать разработчику\n' \
                        '▫️ Удалить себя из бота'

    change_college_group__section = '▫️ Группы друзей - группы, которые добавил/а\n' \
                                    '▫️ Редактирование групп - добавить новую или удалить\n\n' \
                                    'Сейчас ты смотришь расписание у: {group}'
    send_feedback__section = '▫️ По поводу работы бота: баги, предложения. Пиши через бота.\n' \
                             '▫️ Если что-то иное, нашили в личку'
    # Расписание пар #
    select_timetable = 'Выбери расписание, которое хочешь посмотреть: '
    selected_old_timetable = 'Не забудь, что выбрано расписание на текущую неделю!'
    selected_new_timetable = 'Выбрано расписание на следующую неделю!'

    delimiter = '___✂️___'
    timetable_for_days_of_week = 'Смотрим расписание по дням недели 👀'

    today__when = 'Сегодня'
    tomorrow__when = 'Завтра'
    week__when = 'Выходной'
    weekend__when = '{when} выходной!'

    college_group = '📚 {}\n\n'
    day_of_week = '📅 {day_of_week} ({date_str})\n\n'
    timetable_for_one_day = '▪️ {number} пара [{time}]\n' \
                            '📖 {subject}\n' \
                            '👨‍🏫  {teacher} / {cabinet}\n' \
                            '🏫 ({college_building})\n\n'
    weekend = 'В этот день выходной!\n\n'
    break_timetable = '---⏰---\n' \
                      '1. 8.00-9.10\n' \
                      '2. 9.20-10.30\n' \
                      '3. 10.50-12.00\n' \
                      '4. 12.10-13.20\n' \
                      '5. 13.30-14.40\n' \
                      '6. 15.00-16.10\n' \
                      '7. 16.20-17.30\n' \
                      '8. 17.40-18.50\n\n' \
                      '🚬  Большие перемены между:\n' \
                      '▫️ 2 и 3 (10.30-10.50)\n' \
                      '▫️ 5 и 6 (14.40-15.00)'

    timetable_is_old = 'Внимание! Это расписание не на следующую неделю.'

    new_timetable_on = '📖 Новое расписание\n' \
                       '📅 с {} по {}'

    old_timetable = '💀 СТАРОЕ 💀\n\n'
    new_timetable = '🔥 НОВОЕ 🔥\n\n'
    warning_timetable_changes = '\n\nВнимание!\n' \
                                'На {date_str}\n' \
                                '✏️📖 Изменения в расписании\n' \
                                '(см. выше 🔺)'
    timetable_changes_for_friends = 'На {date_str}\n\n' \
                                    '✏️📖 Изменения в расписании у твоих друзей:\n' \
                                    '{groups}'
    # Настройки #
    add_first_group = 'Добавь группы своих друзей, чтобы смотреть их расписание'
    new_group__first = 'Ты можешь добавить не больше 6 групп.\n' \
                       'Напиши группу, следуя примеру: П-419/2'
    new_group__second = 'Ты можешь добавить не больше 6 групп.\n' \
                        'Уже добавлены: {groups}\n\n' \
                        'Напиши группу, следуя примеру: П-419/2'
    added_groups = 'Уже добавлены: {}'
    group_added = 'Группа добавлена!'
    saved_groups = '🤙📚Группы друзей:\n\n' \
                   'Кликни по кнопке, чтобы перейти в эту группу и посмотреть расписание'
    edit_groups = 'Только не спрашивай: "Кстати, а почему лимит в 6 групп?"'
    secret_question = 'Кстати, а почему лимит в 6 групп?'
    delete_groups = 'Кликни по группе, которую хочешь удалить:'
    group_deleted = 'Группа удалена!'

    send_message_to_lucifer = \
        'Тут ты можешь написать любое текстовое сообщение и отправить его мне. Но только раз в час!\n\n' \
        'Если нашел баг, то сообщи мне о нем, например так: "<i>Баг в разделе расписания, нажимаю на кнопку ' \
        '"Расписание на сегодня", но ничего не происходит</i>".\n\n' \
        'Хочу снять с себя немного ответственности за работу бота. В расписании' \
        '(кстати, формат файлов с расписанием поддерживался до 2008 года, поэтому у кого-то расписание не открывается) ' \
        'встречаются опечатки, например, нет кабинета. Поэтому в расписании, которое отправляет бот, могут встречаться ' \
        'ошибки/опечатки. Я стараюсь их все находить, но все отловить невозможно :)\n' \
        'Мой человеческий фактор и администрации.\n\n\n' \
        'Если есть идеи насчет бота, то предложи тут.'
    private_message = 'Мой тг: @anondoom'
    message_sent = 'Сообщение отправлено!'

    delete_account = 'Уверен, что хочешь удалить себя из бота?'
    deleted_account = 'Я вижу, что ты хочешь смотреть расписание в excel файле, который:\n' \
                      '- иногда не открывается \n' \
                      '- листать до своей группы, потом мотать в начало, чтобы посмотреть время пар, потом обратно ' \
                      'на свою группу и тд.\n' \
                      '- делать скрины расписания\n\n\n' \
                      'Вместо того, чтобы кликнуть по паре\nкнопок и:\n' \
                      '1) детальное\n' \
                      '2) красивое \n' \
                      '3) удобное расписание\n' \
                      'будет перед твоими глазами!'


class BotButtons:
    """
    Класс со всеми кнопками.
    """
    # Общее #
    back = 'Назад'
    back_to_settings = '⚙ Назад к настройкам'
    back_to_main_menu = '🏠 Назад в главное меню'
    back_to_timetable = '📖 Назад к расписанию'

    back_to_timetable_section = '📖 Назад в раздел расписания'
    back_to_choose_college_building = '🏫 Назад к выбору корпуса'

    yes = 'Да'
    no = 'Нет'
    confirm_your_action__markup = [yes, no, back]

    # Создатель #
    owner_role = '🧛🏻 Owner Role'

    change_role = '👨🏼‍🎓🧙🏼‍♂️ Change role'
    owners = '🧛🏻 Owners'
    deploy = '👨🏽‍💻 Deploy'
    owner_main_menu__markup = [change_role, owners, deploy]

    user_role = '👨🏼‍🎓 User Role'
    admin_role = '🧙🏼‍♂️ Admin Role'
    change_role__markup = [user_role, admin_role, back_to_main_menu]

    add_owner = '➕🧛🏻 Add owner'
    delete_owner = '➖🧛🏻 Delete owner'
    owners_section__markup = [add_owner, delete_owner, back_to_main_menu]

    truncate_storages = '🗑 Truncate storages'
    add_groups = '➕📚 Add groups'
    fill_redis = '📝 Fill Redis'
    deploy_section__markup = [truncate_storages, add_groups, fill_redis, back_to_main_menu]

    # Админ #
    admin_timetable = '📖 Расписание'
    bots_admins = '🧙🏼‍♂️ Админы бота'
    admin_main_menu__markup = [admin_timetable, bots_admins]

    add_timetable = '➕📖 Новое'
    timetable_changes = '✏️📖 Изменения'
    admin_timetable__markup = [add_timetable, timetable_changes, back_to_main_menu]

    one_college_building = '🏫 Одного корпуса'
    two_college_building = '🏫🏫 Двух корпусов'
    timetable_changes__markup = [one_college_building, two_college_building, back_to_timetable_section]

    college_building_1 = '🏫 Курчатова,16'
    college_building_2 = '🏫 Туполева,17а'
    choose_college_building__markup = [college_building_1, college_building_2, back_to_timetable_section]

    # Юзер (студент) #
    timetable_of_classes = '📖 Расписание пар'
    break_timetable = '🚬 Расписание перемен'
    settings = '⚙️ Настройки'
    user_main_menu__markup = [timetable_of_classes, break_timetable, settings]

    change_college_group = '📚 Сменить группу'
    message_to_the_developer = '👨‍💻 Написать разработчику'
    delete_account = '👎 Удалить аккаунт'
    settings__markup = [change_college_group, message_to_the_developer, delete_account, back_to_main_menu]

    delete_account__yes = '🤡 Да, excel удобнее!'
    delete_account__no = '😻 Нет, бот удобнее!'
    delete_account__markup = [delete_account__yes, delete_account__no, back_to_settings]

    from_bot = '🤖 Через бота'
    private_message = '💌 Личное сообщение'
    send_feedback__markup = [from_bot, private_message, back_to_settings]

    new_group = '➕📚 Добавить группу'
    delete_college_group = '➖📚 Удалить группу'
    add_group__markup = [new_group, back_to_settings]
    edit_group__markup = [new_group, delete_college_group, back]
    edit_group__only_delete__markup = [delete_college_group, back]

    go_to_own_group = '🔙📚 Вернуться на свою группу'
    groups_friends = '🤙📚 Группы друзей'
    edit_groups = '✏️ 📚 Редактирование групп'
    change_group__markup = [groups_friends, edit_groups, back_to_settings]

    go_to_new_group = '📚 Перейти в нее'
    group_added__markup = [go_to_new_group,  back_to_main_menu]

    old_timetable = 'Текущая неделя'
    new_timetable = 'Следующая неделя'
    select_timetable__markup = [old_timetable, new_timetable, back_to_main_menu]

    timetable_for_today = 'Cегодня'
    timetable_for_tomorrow = 'Завтра'
    timetable_for_week = 'Вся неделя'
    timetable_for_day_of_week = 'По дням недели'
    user_timetable__markup = [timetable_for_today, timetable_for_tomorrow, timetable_for_week, timetable_for_day_of_week,
                              back_to_main_menu]

    monday = 'Понедельник'
    tuesday = 'Вторник'
    wednesday = 'Среда'
    friday = 'Пятница'
    saturday = 'Суббота'
    days_of_week__markup = [monday, tuesday, wednesday, friday, saturday]

    reply_markup = {
        # Создатель #
        'owner__main_menu': {'markup': owner_main_menu__markup, 'row_width': 2},
        'change_role': {'markup': change_role__markup, 'row_width': 2},
        'owners__section': {'markup': owners_section__markup, 'row_width': 2},
        'deploy__section': {'markup': deploy_section__markup, 'row_width': 1},
        'confirm_your_action': {'markup': confirm_your_action__markup, 'row_width': 2},


        # Админ #
        'admin__main_menu': {'markup': admin_main_menu__markup, 'row_width': 2},
        'admin_timetable': {'markup': admin_timetable__markup, 'row_width': 2},

        'timetable_changes': {'markup': timetable_changes__markup, 'row_width': 2},
        'choose_college_building': {'markup': choose_college_building__markup, 'row_width': 2},


        # Юзер #
        'user__main_menu': {'markup': user_main_menu__markup, 'row_width': 2},

        # Расписание #
        'select_timetable': {'markup': select_timetable__markup, 'row_width': 2},
        'user_timetable': {'markup': user_timetable__markup, 'row_width': 2},

        # Настройки #
        'send_feedback': {'markup': send_feedback__markup, 'row_width': 2},
        'delete_account': {'markup': delete_account__markup, 'row_width': 2},

        'add_group': {'markup': add_group__markup, 'row_width': 1},
        'group_added': {'markup': group_added__markup, 'row_width': 2},

        'change_group': {'markup': change_group__markup, 'row_width': 2},
        'edit_group': {'markup': edit_group__markup, 'row_width': 2},
        'edit_group__only_delete': {'markup': edit_group__only_delete__markup, 'row_width': 1},
    }


class BotErrors:
    """
    Класс с ошибками во время работы бота.
    """
    # Создатель #
    user_id_value_error = 'Должен быть числом!'
    you_cant_add_yourself = 'Нельзя добавить самого себя!'
    you_cant_delete_yourself = 'Нельзя удалить самого себя!'
    you_have_already_added_this_user = 'Этот человек уже есть!'
    this_person_not_found = 'Этого человека нет!'
    you_cant_delete_lucifer = 'Нельзя удалить Люцифера!'

    # Админ #
    error_in_timetable = 'При чтении расписания произошла ошибка.\nПожалуйста, убедитесь, что в расписании ничего не' \
                         ' пропущено, например, даты, номера пар, время пар и тд.\n\n' \
                         'После этого заново отправьте файл:'
    received_one_excel_file = 'Я ожидаю получить группу из двух файлов'

    timetable_is_already_there = 'Расписание c таким же временем уже есть!'

    # Юзер #
    college_group_not_found = 'Группа не найдена..'

    day_of_week_is_sunday = '{when} воскресенье :)'
    still_no_timetable = 'Расписания еще нет..\n' \
                         'Как выложат, я тебе сообщу!'

    throttled = 'Все. Сообщение ты уже отправил/а :)\n' \
                'Можно отправлять только раз в час'

    this_is_your_group = 'Это твоя группа...'
    you_have_already_selected_this_group = 'Ты уже смотришь расписание этой группы'
    you_have_already_added_this_group = 'Эта группа уже добавлена'

    delete_own_group = 'Себя удалить хочешь?'
