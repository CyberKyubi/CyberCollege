from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminStates(StatesGroup):
    pass


class UserStates(StatesGroup):
    select_college_group = State()

    main_menu = State()