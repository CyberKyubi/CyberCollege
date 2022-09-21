from aiogram.dispatcher.filters.state import StatesGroup, State


class OwnerMainMenuStates(StatesGroup):
    main_menu = State()


class DeployStates(StatesGroup):
    excel_file_input = State()
