from typing import List, Dict, Tuple

from sqlalchemy.dialects.postgresql import insert, array_agg
from sqlalchemy import select
from sqlalchemy.sql.expression import func

from .models import Users, CollegeGroups


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


async def insert__new_user(session_pool, user_id: int, college_group: str, college_building: str):
    async with session_pool() as session:
        await session.execute(
            insert(Users)
            .values(user_id=user_id, college_group=college_group, college_building=college_building)
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


async def truncate__tables(session_pool):
    async with session_pool() as session:
        await session.execute("TRUNCATE college_groups RESTART IDENTITY CASCADE")
        await session.execute("TRUNCATE users RESTART IDENTITY")
        await session.commit()


async def insert__college_groups(session_pool, groups: list):
    async with session_pool() as session:
        await session.execute(
            insert(CollegeGroups)
            .values(groups)
        )
        await session.commit()
