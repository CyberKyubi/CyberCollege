from typing import Optional

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from config import load_config


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, message: Message):
        admins_id = load_config().tgbot.admins_id
        return message.from_user.id in admins_id