import asyncio
from typing import Dict, Tuple

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.dispatcher.storage import FSMContext

from config_reader import config
from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup
from keyboards.inline_keyboard_markup import groups_markup, groups_cd
from states.owner_state_machine import UsersStates, StudentsStates
from handlers.user.settings.delete_account import delete_student
from .get_period import get_period
from storages.redis.storage import RedisStorage
from storages.db.requests import select__all_students, select__all_students_by_building
from utils.validation.get_mention import get_mention
from utils.validation.send_message import send_message
from utils.redis_models.user_data import UserModel
from utils.redis_models.students import GroupModel, CachedGroupModel
from utils.activity.read_logs import read_logs
from utils.activity.enums import LogLevelEnum, RoleEnum, StatementEnum


async def students__section(message: Message, state: FSMContext, session_pool):
    count_students = await select__all_students(session_pool)

    text = ''
    groups, students = [], []
    for row in count_students:
        _, groups_row, students_row = row
        groups.append(groups_row), students.append(students_row)
        text += BotMessages.students__section % (*row, )
    total = BotMessages.total_students % (sum(groups), sum(students))

    await message.answer(text + total, reply_markup=reply_markup('students'))
    await state.set_state(StudentsStates.students)


async def choice_college_building__send_button(message: Message, state: FSMContext):
    await message.answer(BotMessages.choice_college_building, reply_markup=reply_markup('owner_choice_college_building'))
    await state.set_state(StudentsStates.choice_college_building)


async def back_to_students_section__button(message: Message, state: FSMContext, session_pool):
    await students__section(message, state, session_pool)


async def back_to_choice_college_building__button(message: Message, state: FSMContext):
    await choice_college_building__send_button(message, state)


async def back_to_student_section__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    model = await group_to_model(redis__db_1)
    await current_student__section(message, state, redis__db_1, model.group, model.selected_user.user_id)


async def back_to_list_students__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    model = await group_to_model(redis__db_1)
    msg_to_send, _ = await check_cached_group(message, redis__db_1, model.group)
    await send_list_students_msg(message, state, msg_to_send)


async def back_to_student(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    model = await group_to_model(redis__db_1)
    await current_student__section(message, state, redis__db_1, model.group, model.selected_user.user_id)


async def show_list_groups(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    college_building = message.text[2:]
    students = await select__all_students_by_building(session_pool, college_building)

    if not students:
        await message.answer(BotErrors.students_from_college_building_not_found)
        return

    list_groups = {group: [str(student_id) for student_id in list_students] for group, list_students in students}
    groups = list(list_groups.keys())
    await redis__db_1.set_data('list_groups', list_groups)

    await message.answer(BotMessages.click_on_group, reply_markup=groups_markup(groups))
    await message.answer(
        BotMessages.select_group.format(cb=college_building, groups=len(groups)),
        reply_markup=reply_markup('back_to_choose_college_building', back=True)
    )
    await state.set_state(StudentsStates.select_group)


async def selected_group(
        query: CallbackQuery,
        callback_data: Dict[str, str],
        state: FSMContext,
        redis__db_1: RedisStorage
):
    group = callback_data['button']

    list_groups = await redis__db_1.get_data('list_groups')
    group_model = GroupModel(group=group, list_students=list_groups[group])
    await redis__db_1.set_data('group', group_model.dict())

    msg_to_send, _ = await check_cached_group(query.message, redis__db_1, group)
    await send_list_students_msg(query.message, state, msg_to_send)


async def check_cached_group(message: Message, redis__db_1: RedisStorage, group: str, rewrite=False) -> Tuple[str, dict]:
    key = group + '__cached'
    cached_group = await redis__db_1.get_cached_group(key)
    if not cached_group or rewrite:
        await message.answer(BotMessages.data_is_generated)

        list_groups, users = await redis__db_1.get_multiple_data('list_groups', 'users')
        list_students = list_groups[group]
        users_data = users['users_data']

        cached_group_model = await generate_list_students_msg(message, group, list_students, users_data)
        await redis__db_1.set_cached_group(key, cached_group_model.dict())
    else:
        cached_group_model = CachedGroupModel(**cached_group)

    msg_to_send, list_students__cache = cached_group_model.list_students_msg, cached_group_model.students
    return msg_to_send, list_students__cache


async def generate_list_students_msg(
        message: Message,
        group: str,
        list_students: list,
        users_data: dict
) -> CachedGroupModel:
    list_students_msg = ''
    students = {}
    for number, user_id in enumerate(list_students, 1):
        model = UserModel(**users_data[user_id])
        mention = await get_mention(message, user_id)

        if not model.groups_friends:
            group_friends = BotMessages.group_friends__empty
        else:
            group_friends = ''.join([
                BotMessages.group_friends__not_empty.format(number=number, group=model.group, cb=model.college_building)
                for number, model in enumerate(model.groups_friends, 1)
            ])

        student_msg = BotMessages.student_info.format(
            group=model.default_college_group,
            cb=model.default_college_building,
            group_friends=group_friends,
            username=mention, user_id=user_id
        )
        list_students_msg += BotMessages.student.format(number=number, username=mention, user_id=user_id)
        students[user_id] = student_msg

    msg = BotMessages.students.format(group=group) + list_students_msg + BotMessages.students__end_msg
    return CachedGroupModel(list_students_msg=msg, students=students)


async def send_list_students_msg(message: Message, state: FSMContext, msg: str):
    await message.answer(msg)
    await message.answer(
        BotMessages.select_student, reply_markup=reply_markup('back_to_choose_college_building', back=True)
    )
    await state.set_state(StudentsStates.list_students)


async def selected_student(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    model = await group_to_model(redis__db_1)
    student = message.text

    if student not in model.list_students:
        await message.answer(BotErrors.student_not_found.format(user_id=student))
        return

    model.selected_user.user_id = student
    await redis__db_1.set_data('group', model.dict())
    await current_student__section(message, state, redis__db_1, model.group, student)


async def current_student__section(message: Message, state: FSMContext, redis__db_1: RedisStorage, group: str, user_id: str):
    _, students = await check_cached_group(message, redis__db_1, group)
    student = students[user_id]
    await message.answer(student, reply_markup=reply_markup('student__section'))
    await state.set_state(StudentsStates.current_student)


async def student_activity__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.period_activity, reply_markup=reply_markup('student_activity'))
    await state.set_state(StudentsStates.student_activity)


async def student_activity__output(message: Message, redis__db_1: RedisStorage):
    period = get_period(message.text)
    model = await group_to_model(redis__db_1)
    simple = read_logs(
        role=RoleEnum.user,
        user_id=model.selected_user.user_id,
        level=LogLevelEnum.INFO,
        period=period,
        statement=StatementEnum.one_student
    )

    await message.answer(simple)
    await message.answer_document(InputFile(config.student_activity), caption='Детально')
    await message.answer_document(InputFile(config.all_logline), caption='Все логи')


async def delete_student__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.sent_message_for_deleted_student, reply_markup=reply_markup('back', back=True))
    await state.set_state(StudentsStates.message_for_deleted_student)


async def delete_student__input(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage, dp):
    model = await group_to_model(redis__db_1)

    user_id__str = model.selected_user.user_id
    user_id__int = int(user_id__str)

    list_groups = await redis__db_1.get_data('list_groups')

    await send_message(message, BotMessages.message_for_deleted_student.format(message.text), user_id__int)
    await delete_student(session_pool, redis__db_1, dp, user_id__int)
    await message.answer(BotMessages.student_deleted)

    groups = list(list_groups.keys())
    model.list_students.remove(user_id__str)
    if model.list_students:
        list_groups[model.group].remove(user_id__str)
        await redis__db_1.set_data('list_groups', list_groups)

        msg_to_send, _ = await check_cached_group(message, redis__db_1, model.group, rewrite=True)
        await send_list_students_msg(message, state, msg_to_send)
    else:
        if len(groups) > 1:
            list_groups.pop(model.group)
            await redis__db_1.set_data('list_groups', list_groups)
        else:
            await choice_college_building__send_button(message, state)


async def send_message__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.message_for_student, reply_markup=reply_markup('back', back=True))
    await state.set_state(StudentsStates.message_for_student)


async def send_message__type_text(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    model = await group_to_model(redis__db_1)
    group, user_id = model.group, model.selected_user.user_id

    status = await asyncio.gather(
         send_message(message, BotMessages.message_from_owner, user_id),
         send_message(message, message.text, user_id)
    )
    await message.answer(BotMessages.message_for_student__status.format(*status))
    await current_student__section(message, state, redis__db_1, group, user_id)


async def group_to_model(redis__db_1: RedisStorage) -> GroupModel:
    group = await redis__db_1.get_data('group')
    return GroupModel(**group)


def register_students(dp: Dispatcher):
    dp.register_message_handler(
        students__section,
        text=BotButtons.students,
        state=UsersStates.users
    )

    dp.register_message_handler(
        back_to_students_section__button,
        text=BotButtons.back_to_students_section,
        state=StudentsStates.choice_college_building
    )
    dp.register_message_handler(
        back_to_students_section__button,
        text=BotButtons.back_to_students_section,
        state=StudentsStates.student_activity
    )
    dp.register_message_handler(
        back_to_students_section__button,
        text=BotButtons.back_to_students_section,
        state=StudentsStates.students_activity
    )
    dp.register_message_handler(
        back_to_choice_college_building__button,
        text=BotButtons.back_to_choice_college_building,
        state=StudentsStates.select_group
    )
    dp.register_message_handler(
        back_to_choice_college_building__button,
        text=BotButtons.back_to_choice_college_building,
        state=StudentsStates.list_students
    )
    dp.register_message_handler(
        back_to_list_students__button,
        text=BotButtons.back_to_list_students,
        state=StudentsStates.current_student
    )
    dp.register_message_handler(
        back_to_student_section__button,
        text=BotButtons.back,
        state=StudentsStates.message_for_student
    )
    dp.register_message_handler(
        back_to_student_section__button,
        text=BotButtons.back,
        state=StudentsStates.message_for_deleted_student
    )
    dp.register_message_handler(
        back_to_student,
        text=BotButtons.back_to_student,
        state=StudentsStates.student_activity
    )

    dp.register_message_handler(
        choice_college_building__send_button,
        text=BotButtons.all_students,
        state=StudentsStates.students
    )
    dp.register_message_handler(
        show_list_groups,
        text=[BotButtons.college_building_1, BotButtons.college_building_2],
        state=StudentsStates.choice_college_building
    )
    dp.register_callback_query_handler(
        selected_group,
        groups_cd.filter(),
        state=StudentsStates.select_group
    )
    dp.register_callback_query_handler(
        selected_group,
        groups_cd.filter(),
        state=StudentsStates.list_students
    )
    dp.register_message_handler(
        selected_student,
        content_types=['text'],
        state=StudentsStates.list_students
    )

    dp.register_message_handler(
        delete_student__button,
        text=BotButtons.delete_user,
        state=StudentsStates.current_student
    )
    dp.register_message_handler(
        delete_student__input,
        content_types=['text'],
        state=StudentsStates.message_for_deleted_student
    )

    dp.register_message_handler(
        send_message__button,
        text=BotButtons.send_message,
        state=StudentsStates.current_student
    )
    dp.register_message_handler(
        send_message__type_text,
        content_types=['text'],
        state=StudentsStates.message_for_student
    )
    dp.register_message_handler(
        student_activity__button,
        text=BotButtons.activity,
        state=StudentsStates.current_student
    )
    dp.register_message_handler(
        student_activity__output,
        text=[BotButtons.activity_today, BotButtons.activity_week, BotButtons.activity_month,
              BotButtons.activity_all_time],
        state=StudentsStates.student_activity
    )