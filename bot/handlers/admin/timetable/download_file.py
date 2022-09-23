import asyncio

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from states.owner_state_machine import DeployStates
from states.admin_state_machine import AdminTimetableSectionStates
from storages.redis.storage import RedisStorage
from handlers.admin.timetable.new_timetable import preparing
from handlers.owner.deploy.deploy import add_groups
from config import load_config


async def excel_files__input(message: Message, state: FSMContext, session_pool, redis__db_1: RedisStorage, redis__db_2):
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

    if key == 'file_2':
        await redis__db_1.set_data('files', {'file_1': '', 'file_2': ''})
        await message.answer(BotMessages.received_documents)

        current_state = await state.get_state()
        if current_state in DeployStates:
            await add_groups(files_data, message, state, session_pool, redis__db_1)
        elif current_state in AdminTimetableSectionStates:
            await preparing(files_data, message, state, redis__db_1, redis__db_2)
    else:
        await redis__db_1.set_data('files', files_data)


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


async def download_file(message: Message, file_id: str, destination: str):
    await message.bot.download_file_by_id(file_id, destination)
    return destination


def register_download_file(dp: Dispatcher):
    dp.register_message_handler(
        excel_files__input,
        content_types=['document'],
        state=DeployStates.add_groups
    )
    dp.register_message_handler(
        excel_files__input,
        content_types=['document'],
        state=AdminTimetableSectionStates.new_timetable
    )