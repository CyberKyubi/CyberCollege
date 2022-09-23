from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons
from states.owner_state_machine import OwnerMainMenuStates, DeployStates
from keyboards.reply_keyboard_markup import reply_markup, back_markup
from storages.redis.storage import RedisStorage
from storages.db.requests import truncate__tables, insert__college_groups
from handlers.owner.main_menu.menu import owner__main_menu
from utils.timatable.timetable import Timetable


async def deploy__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.deploy__section, reply_markup=reply_markup('deploy__section'))
    await state.set_state(DeployStates.deploy)


async def bact_to_main_menu__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await owner__main_menu(message, state, redis__db_1)


async def back__button(message: Message, state: FSMContext):
    await deploy__section(message, state)


async def confirm_your_action__send_buttons(message: Message, state: FSMContext):
    await message.answer(
        BotMessages.confirm_your_action.format(action=BotMessages.truncate_storages__action),
        reply_markup=reply_markup('confirm_your_action')
    )
    await state.set_state(DeployStates.confirm_your_action)


async def confirm_your_action__input(
        message: Message,
        state: FSMContext,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    if message.text == BotButtons.yes:
        await truncate_storages(message, state, session_pool, redis__db_1, redis__db_2)
    elif message.text == BotButtons.no or message.text == BotButtons.back:
        await deploy__section(message, state)


async def truncate_storages(
        message: Message,
        state: FSMContext,
        session_pool,
        redis__db_1: RedisStorage,
        redis__db_2: RedisStorage
):
    await truncate__tables(session_pool)

    await redis__db_1.delete_all_data()
    await redis__db_2.delete_all_data()

    await message.answer(BotMessages.storages_cleared)
    await deploy__section(message, state)


async def add_groups__section(message: Message, state: FSMContext):
    await message.answer(BotMessages.excel_files, reply_markup=back_markup())
    await state.set_state(DeployStates.add_groups)


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


async def fill_redis(message: Message, redis__db_1: RedisStorage):
    users = {'users_data': {}, 'users_id': []}
    await redis__db_1.set_data('users', users)

    await message.answer(BotMessages.redis_is_ready)


def register_deploy__section(dp: Dispatcher):
    dp.register_message_handler(
        deploy__section,
        text=BotButtons.deploy,
        state=OwnerMainMenuStates.main_menu
    )

    dp.register_message_handler(
        bact_to_main_menu__button,
        text=BotButtons.back_to_main_menu,
        state=DeployStates.deploy
    )
    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=DeployStates.add_groups
    )

    dp.register_message_handler(
        confirm_your_action__send_buttons,
        text=BotButtons.truncate_storages,
        state=DeployStates.deploy
    )
    dp.register_message_handler(
        confirm_your_action__input,
        text=BotButtons.confirm_your_action__markup,
        state=DeployStates.confirm_your_action
    )
    dp.register_message_handler(
        add_groups__section,
        text=BotButtons.add_groups,
        state=DeployStates.deploy
    )
    dp.register_message_handler(
        fill_redis,
        text=BotButtons.fill_redis,
        state=DeployStates.deploy
    )