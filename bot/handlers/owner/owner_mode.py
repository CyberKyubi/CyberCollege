import asyncio

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotButtons, BotMessages
from states.owner_state_machine import OwnerMainMenuStates, DeployStates
from states.user_state_machine import MainMenuStates as AdminStates
from states.admin_state_machine import MainMenuStates as UserStates
from keyboards.reply_keyboard_markup import owner_main_menu_markup, back_to_main_menu
from storages.redis.storage import RedisStorage
from storages.db.requests import insert__college_groups
from handlers.user.main_menu.menu import user__main_menu
from handlers.user.get_user_data import get_current_group
from handlers.admin.main_menu.menu import admin__main_menu
from handlers.admin.timetable.section import download_file
from utils.timatable.timetable import Timetable
from config import load_config


async def owner__main_menu(message: Message, state: FSMContext):
    await message.answer(BotMessages.owner__main_menu, reply_markup=owner_main_menu_markup())
    await state.set_state(OwnerMainMenuStates.main_menu)


async def back_to_main_menu__button(message: Message, state: FSMContext):
    await owner__main_menu(message, state)


async def alter_role_admin_to_user(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    _, college_group = await get_current_group(message.from_user.id, redis__db_1)
    await set_current_role(str(message.from_user.id), 'User', redis__db_1)
    await user__main_menu(message, state, college_group)


async def alter_tole_user_to_admin(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await set_current_role(str(message.from_user.id), 'Admin', redis__db_1)
    await admin__main_menu(message, state)


async def deploy__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.excel_file_input, reply_markup=back_to_main_menu())
    await state.set_state(DeployStates.excel_file_input)


async def deploy__input(
        message: Message,
        state: FSMContext,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage,
        album: list
):
    paths = [load_config().excel_file_1, load_config().excel_file_2]
    finished, pending = await asyncio.wait(
        [download_file(message, document.file_id, path) for document, path in zip(album, paths)]
    )
    if pending:
        await asyncio.sleep(0.3)

    await deploy(finished, message, state, session_pool, redis__db_1, redis__db_2)


async def deploy(
        finished,
        message: Message,
        state: FSMContext,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    await redis__db_1.delete_all_data()
    await redis__db_2.delete_all_data()

    paths = [task.result() for task in finished]
    college_groups__redis, college_groups__db = {}, []
    for path in paths:
        redis, db = Timetable(path).get_groups()
        college_groups__redis.update(redis), college_groups__db.extend(db)

    await redis__db_1.set_data('college_groups', college_groups__redis)
    await insert__college_groups(session_pool, college_groups__db)

    await message.answer(BotMessages.deploy)
    await owner__main_menu(message, state)


async def set_current_role(owner_id: str, role: str, redis__db_1: RedisStorage):
    owners_data = await redis__db_1.get_data('owners')
    owner = owners_data.get(owner_id, {})
    owner.update(role=role)
    owners_data[owner_id] = owner
    await redis__db_1.set_data('owners', owners_data)


def register_owner_mode(dp: Dispatcher):
    dp.register_message_handler(
        owner__main_menu,
        text=BotButtons.owner_mode,
        state=AdminStates.main_menu,
        is_owner=True
    )
    dp.register_message_handler(
        owner__main_menu,
        text=BotButtons.owner_mode,
        state=UserStates.main_menu,
        is_owner=True
    )

    dp.register_message_handler(
        back_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=DeployStates.all_states
    )

    dp.register_message_handler(
        alter_role_admin_to_user,
        text=BotButtons.user_mode,
        state=OwnerMainMenuStates.main_menu,
        is_owner=True
    )
    dp.register_message_handler(
        alter_tole_user_to_admin,
        text=BotButtons.admin_mode,
        state=OwnerMainMenuStates.main_menu,
        is_owner=True
    )

    dp.register_message_handler(
        deploy__button,
        text=BotButtons.deploy,
        state=OwnerMainMenuStates.main_menu
    )
    dp.register_message_handler(
        deploy__input,
        content_types=['document'],
        state=DeployStates.excel_file_input
    )
