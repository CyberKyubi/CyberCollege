import logging

from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages, BotButtons, BotErrors
from keyboards.reply_keyboard_markup import reply_markup
from states.owner_state_machine import UsersStates, OwnersSectionStates
from storages.redis.storage import RedisStorage
from handlers.owner.main_menu.menu import owner__main_menu
from handlers.owner.change_role.set_role import set_current_role
from utils.validation.send_message import send_message
from utils.validation.get_mention import get_mention
from utils.jsons.work_with_json import read_json, write_json
from utils.redis_models.owner import Roles
from config_reader import app_config


async def owners__section(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Раздел с owners roles.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"Owner [{message.from_user.id}] | перешел в owners__section.")
    owners_data = await redis__db_1.get_data('owners')

    msg = BotMessages.owner__section
    for number, user_id__str in enumerate(owners_data.keys(), 1):
        user_id = int(user_id__str)
        mention = await get_mention(message, user_id)
        msg += BotMessages.owner.format(number=number, mention=mention, user_id=user_id)

    await message.answer(msg, reply_markup=reply_markup('owners__section'))
    await state.set_state(OwnersSectionStates.owners)


async def back__button(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    await owners__section(message, state, redis__db_1)


async def add_owner__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.add_owner, reply_markup=reply_markup('back', back=True))
    await state.set_state(OwnersSectionStates.add_owner)


def user_id_str_to_int(user_id__str):
    """
    Меняет str type на int
    :param user_id__str:
    :return:
    """
    try:
        user_id__int = int(user_id__str)
    except ValueError:
        return 'error'
    else:
        return user_id__int


async def add_owner__insert(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Добавляет нового человека в owner role.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"Owner [{message.from_user.id}] | добавляю нового человека в owner role.")
    file = 'owners.json'

    ids = read_json(file)
    user_id__str = message.text
    user_id__int = user_id_str_to_int(user_id__str)

    if isinstance(user_id__int, str):
        await message.answer(BotErrors.user_id_value_error)
        logging.error(f"Ошибка при добавлении нового человека в owner role "
                      f"| Owner [{message.from_user.id}] | input {[message.text]} "
                      f"| msg [{BotErrors.user_id_value_error}] ")
        return

    if user_id__int == message.from_user.id:
        await message.answer(BotErrors.you_cant_add_yourself)
        logging.error(f"Ошибка при добавлении нового человека в owner role "
                      f"| Owner [{message.from_user.id}] | input {[message.text]} "
                      f"| msg [{BotErrors.you_cant_add_yourself}] ")
        return

    if user_id__int in ids:
        await message.answer(BotErrors.you_have_already_added_this_user)
        logging.error(f"Ошибка при добавлении нового человека в owner role "
                      f"| Owner [{message.from_user.id}] | input {[message.text]} "
                      f"| msg [{BotErrors.you_have_already_added_this_user}] ")
        return

    await set_current_role(user_id__str, Roles.user, redis__db_1)
    ids.append(user_id__int)
    write_json(file, ids)
    logging.info(f"Owner [{message.from_user.id}] | добавил [{user_id__str}] в owner role.")

    await send_message(message, BotMessages.you_have_been_added_to_owner_role, user_id__int)
    await message.answer(BotMessages.owner_added)
    await owner__main_menu(message, state, redis__db_1)


async def delete_owner__button(message: Message, state: FSMContext):
    await message.answer(BotMessages.delete_owner, reply_markup=reply_markup('back', back=True))
    await state.set_state(OwnersSectionStates.delete_owner)


async def delete_owner__insert(message: Message, state: FSMContext, redis__db_1: RedisStorage):
    """
    Удаляет человека из owner role.
    :param message:
    :param state:
    :param redis__db_1:
    :return:
    """
    logging.info(f"Owner [{message.from_user.id}] | удаляет человека из owner role.")
    file = 'owners.json'

    ids = read_json(file)
    user_id__str = message.text
    user_id__int = user_id_str_to_int(user_id__str)

    if isinstance(user_id__int, str):
        await message.answer(BotErrors.user_id_value_error)
        logging.error(f"Ошибка при удалении человека из owner role "
                      f"| Owner [{message.from_user.id}] | input {[message.text]} "
                      f"| msg [{BotErrors.user_id_value_error}] ")
        return

    if user_id__int == message.from_user.id:
        await message.answer(BotErrors.you_cant_delete_yourself)
        logging.error(f"Ошибка при удалении человека из owner role "
                      f"| Owner [{message.from_user.id}] | input {[message.text]} "
                      f"| msg [{BotErrors.you_cant_delete_yourself}] ")
        return

    if user_id__int not in ids:
        await message.answer(BotErrors.this_person_not_found)
        logging.error(f"Ошибка при удалении человека из owner role "
                      f"| Owner [{message.from_user.id}] | input {[message.text]} "
                      f"| msg [{BotErrors.this_person_not_found}] ")
        return

    if user_id__int == app_config.lucifer_id:
        await message.answer(BotErrors.you_cant_delete_lucifer)
        logging.error(f"Ошибка при удалении человека из owner role "
                      f"| Owner [{message.from_user.id}] | input {[message.text]} "
                      f"| msg [{BotErrors.you_cant_delete_lucifer}] ")
        return

    owners_data = await redis__db_1.get_data('owners')
    owners_data.pop(user_id__str)
    await redis__db_1.set_data('owners', owners_data)

    ids.remove(user_id__int)
    write_json(file, ids)
    logging.info(f"Owner [{message.from_user.id}] | удалил [{user_id__str}] из owner role.")

    await send_message(message, BotMessages.you_have_been_delete_from_owner_role, user_id__int, ReplyKeyboardRemove())
    await message.answer(BotMessages.owner_added)
    await owner__main_menu(message, state, redis__db_1)


def register_owners__section(dp: Dispatcher):
    dp.register_message_handler(
        owners__section,
        text=BotButtons.owners,
        state=UsersStates.users
    )

    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=OwnersSectionStates.add_owner
    )
    dp.register_message_handler(
        back__button,
        text=BotButtons.back,
        state=OwnersSectionStates.delete_owner
    )

    dp.register_message_handler(
        add_owner__button,
        text=BotButtons.add_owner,
        state=OwnersSectionStates.owners
    )
    dp.register_message_handler(
        add_owner__insert,
        content_types=['text'],
        state=OwnersSectionStates.add_owner
    )
    dp.register_message_handler(
        delete_owner__button,
        text=BotButtons.delete_owner,
        state=OwnersSectionStates.owners
    )
    dp.register_message_handler(
        delete_owner__insert,
        content_types=['text'],
        state=OwnersSectionStates.delete_owner
    )