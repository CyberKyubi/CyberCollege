import logging
from typing import List, Dict, Tuple

from sqlalchemy.dialects.postgresql import insert, array_agg
from sqlalchemy import select
from sqlalchemy.sql.expression import func

from .models import Users, CollegeGroups


async def insert__new_user(session_pool, user_id: int, college_group: str, college_building: str):
    """
    Записывает нового студента.
    :param session_pool:
    :param user_id:
    :param college_group:
    :param college_building:
    :return:
    """
    logging.info("Запрос на добавление нового студента | Статус [Будет выполняться]")
    async with session_pool() as session:
        await session.execute(
            insert(Users)
            .values(user_id=user_id, college_group=college_group, college_building=college_building)
        )
        await session.commit()
        logging.info("Запрос на добавление нового студента | Статус [Выполнен]")


async def truncate__tables(session_pool):
    """
    Очищает все таблицы.
    :param session_pool:
    :return:
    """
    logging.info("Запрос на очитку всех таблиц | Статус [Будет выполняться]")
    async with session_pool() as session:
        await session.execute("TRUNCATE college_groups RESTART IDENTITY CASCADE")
        await session.execute("TRUNCATE users RESTART IDENTITY")
        await session.commit()
        logging.info("Запрос на очитку всех таблиц | Статус [Выполнен]")


async def insert__college_groups(session_pool, groups: list):
    """
    Заполняет таблицу с группами.
    :param session_pool:
    :param groups: список с словарями групп.
    Пример: [{'college_groups': 'П-419/2', 'college_building':'Курчатова,16'}]
    :return:
    """
    logging.info("Запрос на внесение групп | Статус [Будет выполняться]")
    async with session_pool() as session:
        await session.execute(
            insert(CollegeGroups)
            .values(groups)
        )
        await session.commit()
        logging.info("Запрос на внесение групп | Статус [Выполнен]")


# Not used #
async def select__user_data(session_pool, user_id: int) -> str:
    async with session_pool() as session:
        response = await session.execute(
            select(Users.college_group, Users.college_building)
            .where(Users.user_id == user_id)
        )
    if response:
        return response.one()


async def select__all_users(session_pool) -> List[Tuple[int, str]]:
    async with session_pool() as session:
        response = await session.execute(
            select(Users.user_id, Users.college_group, Users.college_building)
            .join(CollegeGroups)
            .filter(Users.college_group == CollegeGroups.college_group)
        )
    if response:
        return response.all()


async def select__all_college_groups(session_pool) -> Dict[str, List[str]]:
    async with session_pool() as session:
        response = await session.execute(
            select(CollegeGroups.college_building, func.array_to_string(array_agg(CollegeGroups.college_group), ','))
            .group_by(CollegeGroups.college_building)
        )
    result = {college_building: college_groups.split(',')for college_building, college_groups in response.all()}
    return result
