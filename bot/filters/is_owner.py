from typing import Optional

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from utils.jsons.work_with_json import read_json


class OwnerFilter(BoundFilter):
    key = 'is_owner'

    def __init__(self, is_owner: Optional[bool] = None):
        self.is_owner = is_owner

    async def check(self, message: Message):
        owners = read_json('owners.json')
        return message.from_user.id in owners
