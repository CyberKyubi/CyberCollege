from typing import Optional

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from utils.jsons.work_with_json import read_json


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, message: Message):
        admins = read_json('admins.json')
        return message.from_user.id in admins
