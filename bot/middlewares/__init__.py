from aiogram import Dispatcher

from .storages import Storages


def setup_middlewares(dp: Dispatcher, session_pool, redis_pool__db_1, redis_pool__db_2):
    dp.setup_middleware(Storages(session_pool, redis_pool__db_1, redis_pool__db_2))