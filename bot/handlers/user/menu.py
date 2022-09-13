from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from locales.ru import BotMessages
from keyboards.reply_keyboard_markup import reply_markup
from states.state_machine import UserStates


async def users__menu(message: Message, state: FSMContext):
    await message.answer(BotMessages.user__main_menu, reply_markup=reply_markup('timetable'))
    await state.set_state(UserStates.main_menu)
