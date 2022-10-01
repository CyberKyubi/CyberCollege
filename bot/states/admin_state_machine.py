from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenuStates(StatesGroup):
    main_menu = State()


class AdminTimetableSectionStates(StatesGroup):
    timetable = State()
    new_timetable = State()


class TimetableChangesStates(StatesGroup):
    number_of_college_building = State()
    choose_college_building = State()
    one_college_building = State()
    two_college_building = State()
    timetable_changes = State()
