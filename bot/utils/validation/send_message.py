import logging
import asyncio

from aiogram.types import Message
from aiogram.utils.exceptions import ChatNotFound, BotBlocked, UserDeactivated, RetryAfter, TelegramAPIError


async def send_message(message: Message, message_to_send: str, user_id: int, reply_markup=None):
    try:
        await asyncio.sleep(0.4)
        message_from_bot = await message.bot.send_message(
            chat_id=user_id, text=message_to_send, reply_markup=reply_markup
        )
    except ChatNotFound:
        logging.error(f'Отправка сообщения студенту от лица бота | Чат [{user_id}] не был найден.')
    except BotBlocked:
        logging.error(f'Отправка сообщения студенту от лица бота | Пользователь [{user_id}] заблокировал бота.')
    except UserDeactivated:
        logging.error(f'Отправка сообщения студенту от лица бота | Пользователь [{user_id}] удален.')
    except RetryAfter as e:
        logging.error(f'Отправка сообщения студенту от лица бота | Флуд лимит превышен. Sleep {e.timeout} seconds.')
        await asyncio.sleep(e.timeout)
        return await send_message(message, message_to_send, user_id, reply_markup)
    except TelegramAPIError as e:
        logging.error(f'Отправка сообщения студенту от лица бота | Неуспешно [{e}]')
    else:
        logging.info(f'Отправка сообщения студенту от лица бота | Успешно [{message_from_bot}]')