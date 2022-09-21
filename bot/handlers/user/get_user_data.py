from typing import List

from storages.redis.storage import RedisStorage
from utils.json_models.user_data import UserModel


async def get_current_group(user_id: int, redis__db_1: RedisStorage, selected_timetable=False) -> List[str]:
    user_model = await to_model(user_id, redis__db_1)
    value_to_return = [user_model.current_group.college_building, user_model.current_group.group]
    if selected_timetable:
        value_to_return.append(user_model.selected_timetable)
    return value_to_return


async def get_default_values(user_id: int, redis__db_1: RedisStorage):
    user_model = await to_model(user_id, redis__db_1)
    return user_model.default_college_group, user_model.default_college_building


async def to_model(user_id: int, redis__db_1: RedisStorage) -> UserModel:
    users = await redis__db_1.get_data('users')
    users_data = users['users_data']
    user_id__str = str(user_id)
    return UserModel(**users_data[user_id__str])