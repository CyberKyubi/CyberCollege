from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenuStates(StatesGroup):
    main_menu = State()


class AdminTimetableSectionStates(StatesGroup):
    timetable = State()
    new_timetable = State()
