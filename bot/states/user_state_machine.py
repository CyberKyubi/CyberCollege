from aiogram.dispatcher.filters.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    college_group__input = State()


class MainMenuStates(StatesGroup):
    main_menu = State()


class UserTimetableSectionStates(StatesGroup):
    timetable = State()
    select_timetable = State()
    days_of_week = State()


class SettingsSectionStates(StatesGroup):
    settings = State()
    feedback = State()
    send_message = State()
    delete_account = State()


class ChangeCollegeGroupStates(StatesGroup):
    add_first_group = State()
    new_group__first = State()

    menu = State()
    groups_friends = State()
    new_group__second = State()
    edit_groups = State()
    delete_groups = State()