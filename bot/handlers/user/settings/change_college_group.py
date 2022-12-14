import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup, change_group__with_own_markup, groups_friends_markup
from states.user_state_machine import SettingsSectionStates, ChangeCollegeGroupStates
from storages.redis.storage import RedisStorage
from handlers.user.main_menu.menu import user__main_menu
from handlers.user.get_user_data import to_model
from utils.redis_models.user_data import UserModel, GroupInfoModel


async def change_college_group__section(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Раздел для смены группы.
    Если список друзей пустой, то отправляется разметка с добавлением новой группы.
    Если текущая группа студента равна его собственной, то отправляется разметка по умолчанию с кнопкой,
    чтобы вернуться в свою группу.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Группы друзей]")
    user_model = await to_model(message.from_user.id, redis__db_1)

    # Проверка 1. Если список групп друзей пустой. #
    if not user_model.groups_friends:
        await message.answer(BotMessages.add_first_group, reply_markup=reply_markup('add_group'))
        await state.set_state(ChangeCollegeGroupStates.add_first_group)
        return

    # Проверка 2. Если текущая группа не равна группе, в которой он учится. #
    if user_model.current_group.group != user_model.default_college_group:
        keyboard = change_group__with_own_markup()
    else:
        keyboard = reply_markup('change_group')

    await message.answer(
        BotMessages.change_college_group__section.format(group=user_model.current_group.group),
        reply_markup=keyboard
    )
    await state.set_state(ChangeCollegeGroupStates.menu)


async def back__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await change_college_group__section(message, state, redis__db_1)


async def back_to_edit_groups__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await edit_groups__section(message, state, redis__db_1)


async def add_first_group__button(message: Message, state: FSMContext):
    """
    Обрабатывает кнопку для добавления первой группы друга.
    :param message:
    :param state:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Действие | [Будет добавлять первую группу друга]")
    await message.answer(BotMessages.new_group__first, reply_markup=reply_markup('back_to_settings', back=True))
    await state.set_state(ChangeCollegeGroupStates.new_group__first)


async def add_second_group__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Обрабатывает кнопку для добавления следующих групп друзей.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Действие | [Будет добавлять группу друга]")
    user_model = await to_model(message.from_user.id, redis__db_1)
    groups = ', '.join([groups.group for groups in user_model.groups_friends])
    await message.answer(BotMessages.new_group__second.format(groups=groups), reply_markup=reply_markup('back', back=True))
    await state.set_state(ChangeCollegeGroupStates.new_group__second)


async def new_group__insert(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Получает группу, проверяет ее, если она есть, если уже нет в списке групп, то добавляет в список групп друзей.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Добавить группу]")
    college_groups_data, users = await redis__db_1.get_multiple_data('college_groups', 'users')
    group = message.text

    if group in college_groups_data['Туполева,17а']:
        college_building = 'Туполева,17а'
    elif group in college_groups_data['Курчатова,16']:
        college_building = 'Курчатова,16'
    else:
        await message.answer(BotErrors.college_group_not_found)
        logging.error(f"Ошибка при добавлении группы друга "
                      f"| User | {message.from_user.id} | input {[message.text]} "
                      f"| msg [{BotErrors.college_group_not_found}] ")
        return

    user_id = str(message.from_user.id)
    user_data = users['users_data'][user_id]
    user_model = UserModel(**user_data)

    if group == user_model.default_college_group:
        await message.answer(BotErrors.this_is_your_group)
        logging.error(f"Ошибка при добавлении группы друга "
                      f"| User | {message.from_user.id} | input {[message.text]} "
                      f"| msg [{BotErrors.this_is_your_group}] ")
        return

    if user_model.groups_friends:
        groups = [groups.group for groups in user_model.groups_friends]
        if group in groups:
            await message.answer(BotErrors.you_have_already_added_this_group)
            logging.error(f"Ошибка при добавлении группы друга "
                          f"| User | {message.from_user.id} | input {[message.text]} "
                          f"| msg [{BotErrors.you_have_already_added_this_group}] ")
            return

    user_model.groups_friends.append(GroupInfoModel(college_building=college_building, group=group))
    user_model.group_added = group
    user_data.update(user_model.dict())
    await redis__db_1.set_data('users', users)
    logging.info(f"User | {message.from_user.id} | Действие | [Добавил группу друга] -> {group}")

    await message.answer(BotMessages.group_added)
    await change_college_group__section(message, state, redis__db_1)


async def go_to_own_group__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    logging.info(f"User | {message.from_user.id} | Действие | [Вернулся на свою группу]")
    group = await go_to_group(message, redis__db_1, own_group=True)
    await user__main_menu(message, state, group)


async def go_to_group(
        message: Message,
        redis__db_1: RedisStorage,
        new_group=False,
        own_group=False,
        selected_group=False
) -> str:
    """
    Переходит в указанную группу: новую, свою, выбранную.
    :param message:
    :param redis__db_1:
    :param new_group: Если новая группа.
    :param own_group: Если собственная группа.
    :param selected_group: Если выбранная группа.
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Действие | [Будет переходить на группу друга]")
    users = await redis__db_1.get_data('users')
    user_id = str(message.from_user.id)
    user_data = users['users_data'][user_id]
    user_model = UserModel(**user_data)

    if new_group or selected_group:
        condition = ''
        if new_group:
            condition = user_model.group_added
        elif selected_group:
            condition = selected_group

        group_info = [group_info for group_info in user_model.groups_friends if group_info.group == condition]
        user_model.current_group.college_building = group_info[0].college_building
        user_model.current_group.group = group_info[0].group

    if own_group:
        user_model.current_group.college_building = user_model.default_college_building
        user_model.current_group.group = user_model.default_college_group

    logging.info(f"User | {message.from_user.id} | Действие | [Перешел на группу] -> {user_model.current_group.group}")
    user_data.update(user_model.dict())
    await redis__db_1.set_data('users', users)
    return user_model.current_group.group


async def groups_friends__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Отправляет кнопки с группами друзей.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Переход | раздел [Выбор группы]")
    user_model = await to_model(message.from_user.id, redis__db_1)
    groups = [groups.group for groups in user_model.groups_friends]
    await message.answer(BotMessages.saved_groups, reply_markup=groups_friends_markup(groups))
    await state.set_state(ChangeCollegeGroupStates.groups_friends)


async def groups_friends__insert(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Обрабатывает группу и переходит в нее.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Действие | [Выбрал группу]")
    user_model = await to_model(message.from_user.id, redis__db_1)
    groups_friends = [groups.group for groups in user_model.groups_friends]
    group = message.text
    if group not in groups_friends:
        await message.answer(BotErrors.college_group_not_found)
        logging.error(f"Ошибка при выборе группы "
                      f"| User | {message.from_user.id} | input {[message.text]} "
                      f"| msg [{BotErrors.college_group_not_found}].")
        return

    if group == user_model.current_group.group:
        await message.answer(BotErrors.you_have_already_selected_this_group)
        logging.error(f"Ошибка при выборе группы "
                      f"| User | {message.from_user.id} | input {[message.text]} "
                      f"| msg [{BotErrors.you_have_already_selected_this_group}].")
        return

    await go_to_group(message, redis__db_1, group)
    await user__main_menu(message, state, group)


async def edit_groups__section(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Отправляет разметку, если кол-во групп не превышает лимиту(6), то кнопки: Добавить, Удалить.
    Иначе только: Удалить.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f'User | {message.from_user.id} | Переход | раздел [Редактировать группы]')
    user_model = await to_model(message.from_user.id, redis__db_1)
    keyboard = reply_markup('edit_group')
    if len(user_model.groups_friends) == 6:
        keyboard = reply_markup('edit_group__only_delete')

    await message.answer(BotMessages.edit_groups, reply_markup=keyboard)
    await state.set_state(ChangeCollegeGroupStates.edit_groups)


async def delete_groups__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Отправляет кнопки с группами друзей.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f'User | {message.from_user.id} | Переход | раздел [Удалить группу]')
    user_model = await to_model(message.from_user.id, redis__db_1)
    groups = [groups.group for groups in user_model.groups_friends]
    await message.answer(BotMessages.delete_groups, reply_markup=groups_friends_markup(groups))
    await state.set_state(ChangeCollegeGroupStates.delete_groups)


async def delete_groups__insert(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Обрабатывает группу и удаляет ее.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"User | {message.from_user.id} | Действие | [Будет удалять группу]")
    users = await redis__db_1.get_data('users')
    user_id = str(message.from_user.id)
    user_data = users['users_data'][user_id]
    user_model = UserModel(**user_data)

    groups_friends = [groups.group for groups in user_model.groups_friends]
    group = message.text
    if group == user_model.default_college_group:
        await message.answer(BotErrors.delete_own_group)
        logging.error(f"Ошибка при удалении группы друга "
                      f"| User | {message.from_user.id} | input {[message.text]} "
                      f"| msg [{BotErrors.delete_own_group}] ")
        return

    if group not in groups_friends:
        await message.answer(BotErrors.college_group_not_found)
        logging.error(f"Ошибка при удалении группы друга "
                      f"| User | {message.from_user.id} | input {[message.text]} "
                      f"| msg [{BotErrors.college_group_not_found}] ")
        return

    for group_info in user_model.groups_friends:
        if group_info.group == group:
            user_model.groups_friends.remove(group_info)

    user_model.current_group.college_building = user_model.default_college_building
    user_model.current_group.group = user_model.default_college_group
    user_data.update(user_model.dict())
    await redis__db_1.set_data('users', users)
    logging.info(f"User | {message.from_user.id} | Действие | [Удалил группу] -> {group}")

    await message.answer(BotMessages.group_deleted)
    await user__main_menu(message, state, user_model.default_college_group)


async def secret_question(message: Message):
    logging.info(f"User | {message.from_user.id} | Действие | [Получил секрет]")
    await message.answer('красивое число :)')


def register_change_college_group(dp: Dispatcher):
    dp.register_message_handler(
        change_college_group__section,
        text=BotButtons.change_college_group,
        state=SettingsSectionStates.settings
    )

    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=ChangeCollegeGroupStates.groups_friends
    )
    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=ChangeCollegeGroupStates.edit_groups
    )
    dp.register_message_handler(
        back_to_edit_groups__button,
        text=BotButtons.back,
        state=ChangeCollegeGroupStates.new_group__second
    )
    dp.register_message_handler(
        back_to_edit_groups__button,
        text=BotButtons.back,
        state=ChangeCollegeGroupStates.delete_groups
    )

    dp.register_message_handler(
        add_first_group__button,
        text=BotButtons.new_group,
        state=ChangeCollegeGroupStates.add_first_group
    )
    dp.register_message_handler(
        new_group__insert,
        content_types=['text'],
        state=ChangeCollegeGroupStates.new_group__first
    )
    dp.register_message_handler(
        new_group__insert,
        content_types=['text'],
        state=ChangeCollegeGroupStates.new_group__second
    )
    dp.register_message_handler(
        go_to_own_group__button,
        text=BotButtons.go_to_own_group,
        state=ChangeCollegeGroupStates.menu
    )
    dp.register_message_handler(
        groups_friends__button,
        text=BotButtons.groups_friends,
        state=ChangeCollegeGroupStates.menu
    )
    dp.register_message_handler(
        groups_friends__insert,
        content_types=['text'],
        state=ChangeCollegeGroupStates.groups_friends
    )
    dp.register_message_handler(
        edit_groups__section,
        text=BotButtons.edit_groups,
        state=ChangeCollegeGroupStates.menu
    )
    dp.register_message_handler(
        secret_question,
        text=BotMessages.secret_question,
        state='*'
    )
    dp.register_message_handler(
        add_second_group__button,
        text=BotButtons.new_group,
        state=ChangeCollegeGroupStates.edit_groups
    )
    dp.register_message_handler(
        delete_groups__button,
        text=BotButtons.delete_college_group,
        state=ChangeCollegeGroupStates.edit_groups
    )
    dp.register_message_handler(
        delete_groups__insert,
        content_types=['text'],
        state=ChangeCollegeGroupStates.delete_groups
    )