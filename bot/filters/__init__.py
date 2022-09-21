from aiogram import Dispatcher

from .is_owner import OwnerFilter
from .is_admin import AdminFilter


def setup_filter(dp: Dispatcher):
    dp.filters_factory.bind(OwnerFilter)
    dp.filters_factory.bind(AdminFilter)