import logging
from logging.config import dictConfig
import asyncio

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from middlewares import setup_middlewares
from handlers import register_handlers
from vkbot.bot import VkBot
from storages.redis.base import RedisPool
from storages.redis.storage import RedisStorage
#from utils.scheduler.scheduler import GetUpdatesFromVk
from utils.logging_config import config as log_conf
from config import load_config as app_config


async def main():
    logging.getLogger(__name__)
    dictConfig(log_conf)

    vk_bot_config = app_config().vkbot
    tg_bot_config = app_config().tgbot

    scheduler = AsyncIOScheduler()
    scheduler.start()

    engine = create_async_engine(app_config().storages.postgresql_dsn, future=True, echo=False)
    session_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Создаю два пула с разным номеров бд:
    # - Первый для хранения данных о users(user_id, college_group), чтобы при вызове команды /start,
    # бот не делал запрос в бд, а забирал из redis'а.
    # - Второй для всех остальных нужд.
    redis_pool__db_1 = RedisPool(app_config().storages.redis_uri__db_1)
    redis_pool__db_2 = RedisPool(app_config().storages.redis_uri__db_2)
    redis_pool_connect__db_1 = await redis_pool__db_1.connect()
    redis_pool_connect__db_2 = await redis_pool__db_2.connect()
    redis_storage__db_1 = RedisStorage(redis_pool_connect__db_1)
    redis_storage__db_2 = RedisStorage(redis_pool_connect__db_2)

    vk_bot = VkBot(
        access_token=vk_bot_config.access_token,
        owner_id=vk_bot_config.owner_id,
        redis=redis_storage__db_2,
        excel_file=app_config().excel_file
    )
    #GetUpdatesFromVk(scheduler).start_job(vk_bot.get_updates)

    bot = Bot(tg_bot_config.token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=RedisStorage2())

    setup_middlewares(dp, session_pool, redis_storage__db_1, redis_storage__db_2)
    register_handlers(dp)

    try:
        logging.warning("Bot started!")
        await dp.start_polling(allowed_updates=["message"])
    except Exception as error:
        logging.error(error)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()

        session = await bot.get_session()
        await session.close()

        logging.warning("All session was closed!")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error('Bot is stopped!')