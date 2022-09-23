import logging
import asyncio

from aiogram.types import Message
from aiogram.utils.exceptions import ChatNotFound, BotBlocked, UserDeactivated, TelegramAPIError, RetryAfter


async def get_mention(message: Message,  user_id: int) -> str:
    try:
        await asyncio.sleep(0.1)
        chat = await message.bot.get_chat(user_id)
        mention = chat.mention
    except ChatNotFound:
        logging.error(f'Получить mention | Чат [{user_id}] не был найден.')
    except BotBlocked:
        logging.error(f'Получить mention | Пользователь [{user_id}] заблокировал бота.')
    except UserDeactivated:
        logging.error(f'Получить mention | Пользователь [{user_id}] удален.')
    except RetryAfter as e:
        logging.error(f'Получить mention | Флуд лимит превышен. Sleep {e.timeout} seconds.')
        await asyncio.sleep(e.timeout)
        return await get_mention(message, user_id)
    except TelegramAPIError as e:
        logging.error(f'Получить mention | Неуспешно [{e}]')
    else:
        logging.info(f'Получить mention | Успешно [{mention}]')
        return mention
    return 'Недоступно'
