from aiogram.types import ReplyKeyboardMarkup

from locales.ru import BotButtons


def reply_markup(key: str):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)
    for button in BotButtons.reply_markup[key]:
        markup.insert(button)
    return markup