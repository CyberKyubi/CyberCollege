from aiogram.dispatcher.filters.state import StatesGroup, State


class OwnerMainMenuStates(StatesGroup):
    main_menu = State()


class ChangeRoleStates(StatesGroup):
    change_role = State()


class OwnersSectionStates(StatesGroup):
    owners = State()
    add_owner = State()
    delete_owner = State()


class DeployStates(StatesGroup):
    deploy = State()
    confirm_your_action = State()

    truncate_storages = State()
    add_groups = State()
    add_first_user = State()
    fill_redis = State()
    add_first_timetable = State()
