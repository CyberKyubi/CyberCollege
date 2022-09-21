import logging
from logging.config import dictConfig
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions

from middlewares import setup_middlewares
from filters import setup_filter
from handlers import register_handlers
from storages.redis.base import RedisPool
from storages.redis.storage import RedisStorage
from utils.logging_config import config as log_conf
from utils.scheduler.scheduler import DeleteOldTimetable
from config import load_config as app_config


async def main():
    logging.getLogger(__name__)
    dictConfig(log_conf)

    tg_bot_config = app_config().tgbot

    engine = create_async_engine(app_config().storages.postgresql_dsn, future=True, echo=False)
    session_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Создаю два пула с разным номеров бд:
    # <> Первый - сервисный, для быстрой работы бота. В нем хранятся данные таблицы users(user_id, college_group)
    # и таблицы college_groups(college_group, college_building).
    # <> Второй для всех остальных нужд.
    redis_pool__db_1 = RedisPool(app_config().storages.redis_uri__db_1)
    redis_pool__db_2 = RedisPool(app_config().storages.redis_uri__db_2)
    redis_pool_connect__db_1 = await redis_pool__db_1.connect()
    redis_pool_connect__db_2 = await redis_pool__db_2.connect()
    redis_storage__db_1 = RedisStorage(redis_pool_connect__db_1)
    redis_storage__db_2 = RedisStorage(redis_pool_connect__db_2)

    scheduler = AsyncIOScheduler()
    scheduler_obj = DeleteOldTimetable(scheduler)
    await scheduler_obj.start_job(redis_storage__db_2)
    scheduler.start()

    bot = Bot(tg_bot_config.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot, storage=RedisStorage2())

    setup_middlewares(dp, session_pool, redis_storage__db_1, redis_storage__db_2)
    setup_filter(dp)
    register_handlers(dp)

    try:
        logging.warning("Bot started!")
        await dp.start_polling(allowed_updates=["message"])
    except Exception as error:
        logging.error(error)
    finally:
        scheduler.shutdown()

        close_all_sessions()

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