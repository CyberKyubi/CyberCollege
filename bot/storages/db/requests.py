from typing import List, Dict, Tuple, Union, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update, delete
from sqlalchemy.sql.expression import func

from .models import Users


async def select__all_users(session_pool) -> List[Tuple[int, str]]:
    async with session_pool() as session:
        response = await session.execute(
            select(Users.tg_user_id, Users.college_group)
        )
    if response:
        return response.all()


async def insert__new_user(session_pool, tg_user_id: int, college_group: str):
    async with session_pool() as session:
        await session.execute(
            insert(Users)
            .values(tg_user_id=tg_user_id, college_group=college_group)
        )
        await session.commit()


async def select__user_data(session_pool, tg_user_id: int) -> str:
    async with session_pool() as session:
        response = await session.execute(
            select(Users.college_group)
            .where(Users.tg_user_id == tg_user_id)
        )
    if response:
        return response.one()[0]