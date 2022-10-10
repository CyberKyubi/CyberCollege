from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from locales.ru import BotButtons


groups_cd = CallbackData('groups', 'button')
go_to_new_timetable_cd = CallbackData('timetable', 'button')


def groups_markup(groups: list):
    markup = InlineKeyboardMarkup(row_width=4)
    for group in groups:
        markup.insert(InlineKeyboardButton(group, callback_data=groups_cd.new(button=group)))
    return markup


def go_to_new_timetable():
    markup = InlineKeyboardMarkup(row_width=1)
    button = BotButtons.go_to_new_timetable
    markup.insert(InlineKeyboardButton(button, callback_data=go_to_new_timetable_cd.new(button=button)))
    return markup
