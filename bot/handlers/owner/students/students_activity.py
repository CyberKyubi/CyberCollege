from aiogram import Dispatcher
from aiogram.types import Message, InputFile
from aiogram.dispatcher.storage import FSMContext

from config_reader import config
from locales.ru import BotMessages, BotButtons, BotActivity
from keyboards.reply_keyboard_markup import reply_markup
from states.owner_state_machine import StudentsStates
from .get_period import get_period
from utils.activity.read_logs import read_logs, new_students
from utils.activity.enums import LogLevelEnum, RoleEnum, StatementEnum


async def students_activity__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.students_activity__section, reply_markup=reply_markup('students_activity'))
    await state.set_state(StudentsStates.students_activity)


async def back__button(message: Message, state: FSMContext):
    await students_activity__section(message, state)


async def new_students__button(message: Message):
    students = new_students()
    text = BotActivity.new_students.format(*[0 if not values else len(values) for values in students.values()])
    await message.answer(text)


async def all_students_activity__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.period_activity, reply_markup=reply_markup('all_student_activity'))
    await state.set_state(StudentsStates.all_students_activity)


async def all_students_activity__output(message: Message):
    period = get_period(message.text)
    simple = read_logs(
        role=RoleEnum.user,
        user_id=None,
        level=LogLevelEnum.INFO,
        period=period,
        statement=StatementEnum.all_students
    )

    await message.answer(simple)
    await message.answer_document(InputFile(config.student_activity), caption='Детально')


def register_students_activity__section(dp: Dispatcher):
    dp.register_message_handler(
        students_activity__section,
        text=BotButtons.activity,
        state=StudentsStates.students
    )

    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=StudentsStates.all_students_activity
    )

    dp.register_message_handler(
        new_students__button,
        text=BotButtons.new_students,
        state=StudentsStates.students_activity
    )
    dp.register_message_handler(
        all_students_activity__button,
        text=BotButtons.all_students_activity,
        state=StudentsStates.students_activity
    )
    dp.register_message_handler(
        all_students_activity__output,
        text=[BotButtons.activity_today, BotButtons.activity_week, BotButtons.activity_month,
              BotButtons.activity_all_time],
        state=StudentsStates.all_students_activity
    )