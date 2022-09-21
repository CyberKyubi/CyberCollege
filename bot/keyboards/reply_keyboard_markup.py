from aiogram.types import ReplyKeyboardMarkup

from locales.ru import BotButtons


def owner_main_menu_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)
    markup.row(BotButtons.user_mode, BotButtons.admin_mode)
    markup.row(BotButtons.deploy)
    return markup


def main_menu_markup(role: str = 'User', alter_role=False):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)
    buttons = BotButtons.user_main_menu__markup
    if role == 'Admin':
        buttons = BotButtons.admin_main_menu__markup
    [markup.insert(button) for button in buttons]

    if alter_role:
        markup.row(BotButtons.owner_mode)
    return markup


def back_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, selective=True)
    markup.add(BotButtons.back)
    return markup


def back_to_settings():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, selective=True)
    markup.add(BotButtons.back_to_settings)
    return markup


def back_to_main_menu():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, selective=True)
    markup.add(BotButtons.back_to_main_menu)
    return markup

def reply_markup(key: str) -> ReplyKeyboardMarkup:
    keyboard = BotButtons.reply_markup[key]
    row_width = keyboard['row_width']

    markup = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True, selective=True)
    [markup.insert(button) for button in keyboard['markup']]
    return markup


def days_of_week_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, selective=True)
    [markup.insert(button) for button in BotButtons.days_of_week__markup]
    markup.row(BotButtons.back_to_timetable)
    return markup


def change_group__with_own_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)
    markup.row(BotButtons.go_to_own_group)
    markup.row(BotButtons.groups_friends, BotButtons.edit_groups)
    markup.row(BotButtons.back_to_settings)
    return markup


def groups_friends_markup(groups: list):
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, selective=True)
    [markup.insert(button) for button in groups]
    markup.row(BotButtons.back)
    return markup