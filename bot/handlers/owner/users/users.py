import logging

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from keyboards.reply_keyboard_markup import reply_markup
from states.owner_state_machine import OwnerMainMenuStates, OwnersSectionStates, UsersStates, StudentsStates
from handlers.owner.main_menu.menu import owner__main_menu


async def users__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.users__section, reply_markup=reply_markup('users'))
    await state.set_state(UsersStates.users)


async def back_to_main_menu__button(message: Message, state: FSMContext, redis__db_1):
    await owner__main_menu(message, state, redis__db_1)


async def back_to_section__button(message: Message, state: FSMContext):
    await users__section(message, state)


def register_users__section(dp: Dispatcher):
    dp.register_message_handler(
        users__section,
        text=BotButtons.users,
        state=OwnerMainMenuStates.main_menu
    )

    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=UsersStates.users
    )

    dp.register_message_handler(
        back_to_section__button,
        text=BotButtons.back_to_users_section,
        state=OwnersSectionStates.owners
    )
    dp.register_message_handler(
        back_to_section__button,
        text=BotButtons.back_to_users_section,
        state=StudentsStates.students
    )
