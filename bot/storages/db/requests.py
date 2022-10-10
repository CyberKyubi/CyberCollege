import logging
from typing import List, Dict, Tuple

from sqlalchemy.dialects.postgresql import insert, array_agg
from sqlalchemy import select, delete
from sqlalchemy.sql.expression import func

from .models import Users, CollegeGroups


async def insert__new_user(session_pool, user_id: int, college_group: str, college_building: str):
    """
    Записывает нового студента
    :param session_pool:
    :param user_id:
    :param college_group:
    :param college_building:
    :return:
    """
    logging.info("Запрос [Добавление нового студента] | Статус [Будет выполняться].")
    async with session_pool() as session:
        await session.execute(
            insert(Users)
            .values(user_id=user_id, college_group=college_group, college_building=college_building)
        )
        await session.commit()
        logging.info("Запрос [Добавление нового студента] | Статус [Выполнен].")


async def truncate__tables(session_pool):
    """
    Очищает все таблицы.
    :param session_pool:
    :return:
    """
    logging.info("Запрос [Очитка всех таблиц] | Статус [Будет выполняться].")
    async with session_pool() as session:
        await session.execute("TRUNCATE college_groups RESTART IDENTITY")
        await session.execute("TRUNCATE users RESTART IDENTITY")
        await session.commit()
        logging.info("Запрос [Очитка всех таблиц] | Статус [Выполнен].")


async def insert__college_groups(session_pool, groups: List[Dict[str, str]]):
    """
    Заполняет таблицу с группами.
    :param session_pool:
    :param groups: список с словарями групп.
    Пример: [{'college_groups': 'П-419/2', 'college_building':'Курчатова,16'}]
    :return:
    """
    logging.info("Запрос [Внесение групп] | Статус [Будет выполняться].")
    async with session_pool() as session:
        await session.execute(
            insert(CollegeGroups)
            .values(groups)
        )
        await session.commit()
        logging.info("Запрос [Внесение групп] | Статус [Выполнен].")


async def delete_user(session_pool, user_id: int):
    """
    Удаляет студента.
    :param session_pool:
    :param user_id:
    :return:
    """
    logging.info(f"Запрос [удаление студента [{user_id}]] | Статус [Будет выполняться].")
    async with session_pool() as session:
        await session.execute(
            delete(Users)
            .where(Users.user_id == user_id)
        )
        await session.commit()
    logging.info(f"Запрос [удаление студента [{user_id}]] | Статус [Выполнен].")


async def select__all_students(session_pool):
    """
    Считает всех студентов по корпусу.
    :param session_pool:
    :return:
    """
    logging.info(f"Запрос [Посчитать всех студентов по корпусу] | Статус [Будет выполняться].")
    async with session_pool() as session:
        response = await session.execute(
            select(Users.college_building, func.count(Users.college_group), func.count(Users.user_id))
            .where(Users.role == 'student')
            .group_by(Users.college_building)
        )
    logging.info(f"Запрос [Посчитать всех студентов по корпусу] | Статус [Выполнен].")
    if response:
        return response.all()


async def select__all_students_by_building(session_pool, college_building: str) -> List[Tuple[int, str, str]]:
    """
    Забирает всех студентов по указанному корпусу.
    :param session_pool:
    :param college_building:
    :return:
    """
    logging.info(f"Запрос [Забрать всех студентов по корпусу] | Статус [Будет выполняться].")
    async with session_pool() as session:
        response = await session.execute(
            select(Users.college_group, array_agg(Users.user_id))
            .where(Users.college_building == college_building, Users.role == 'student')
            .group_by(Users.college_group)
        )
    logging.info(f"Запрос [Забрать всех студентов по корпусу] | Статус [Выполнен].")
    if response:
        return response.all()


# Not used #
async def delete__college_groups(session_pool, groups: list):
    async with session_pool() as session:
        await session.execute(
            delete(CollegeGroups)
            .where(CollegeGroups.college_group.in_(groups))
        )
        await session.commit()


async def select__user_data(session_pool, user_id: int) -> str:
    async with session_pool() as session:
        response = await session.execute(
            select(Users.college_group, Users.college_building)
            .where(Users.user_id == user_id)
        )
    if response:
        return response.one()


async def select__all_college_groups(session_pool) -> Dict[str, List[str]]:
    async with session_pool() as session:
        response = await session.execute(
            select(CollegeGroups.college_building, func.array_to_string(array_agg(CollegeGroups.college_group), ','))
            .group_by(CollegeGroups.college_building)
        )
    result = {college_building: college_groups.split(',')for college_building, college_groups in response.all()}
    return result
