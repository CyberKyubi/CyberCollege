from typing import Optional

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from config import load_config


class OwnerFilter(BoundFilter):
    key = 'is_owner'

    def __init__(self, is_owner: Optional[bool] = None):
        self.is_owner = is_owner

    async def check(self, message: Message):
        owners_id = load_config().tgbot.owners_id
        return message.from_user.id in owners_id