import asyncio

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from states.owner_state_machine import DeployStates
from keyboards.reply_keyboard_markup import back_markup
from storages.redis.storage import RedisStorage
from storages.db.requests import insert__college_groups
from handlers.admin.timetable.section import download_file
from utils.timatable.timetable import Timetable
from .deploy import deploy__section
from config import load_config


async def add_groups__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.excel_files, reply_markup=back_markup())
    await state.set_state(DeployStates.add_groups)


async def back__button(message: Message, state: FSMContext):
    await deploy__section(message, state)


async def excel_files__input(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    files_data = await redis__db_1.get_data('files')
    key, path = '', ''
    if not files_data.get('file_1'):
        key = 'file_1'
        path = load_config().excel_file_1
    elif not files_data.get('file_2'):
        key = 'file_2'
        path = load_config().excel_file_2

    value = await get_path(message, path)
    files_data[key] = value
    await redis__db_1.set_data('files', files_data)

    if key == 'file_2':
        await message.answer(BotMessages.received_documents)
        await redis__db_1.set_data('files', {'file_1': '', 'file_2': ''})
        await add_groups(files_data, message, state, session_pool, redis__db_1)


async def get_path(message: Message, destination):
    task = asyncio.create_task(download_file(message, message.document.file_id, destination))

    pending = [task]
    while pending:
        finished, pending = await asyncio.wait(
            pending,
            return_when=asyncio.ALL_COMPLETED
        )
        result = finished.pop().result()
        return result


async def add_groups(files: dict, message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage):
    paths = list(files.values())
    college_groups__redis, college_groups__db = {}, []
    for path in paths:
        redis, db = Timetable(path).get_groups()
        college_groups__redis.update(redis), college_groups__db.extend(db)

    msg = ''.join(
        [BotMessages.received_groups.format(building=building, groups=', '.join(groups))
         for building, groups in college_groups__redis.items()]
    )
    await message.answer(BotMessages.groups + msg)

    await redis__db_1.set_data('college_groups', college_groups__redis)
    await insert__college_groups(session_pool, college_groups__db)

    await deploy__section(message, state)


def register_add_groups(dp: Dispatcher):
    dp.register_message_handler(
        add_groups__section,
        text=BotButtons.add_groups,
        state=DeployStates.deploy
    )

    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=DeployStates.add_groups
    )

    dp.register_message_handler(
        excel_files__input,
        content_types=['document'],
        state=DeployStates.add_groups
    )