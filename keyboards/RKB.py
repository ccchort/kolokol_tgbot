from aiogram.utils.keyboard import ReplyKeyboardBuilder as builder
from aiogram.types import KeyboardButton as button

class replyKB:

    @staticmethod
    async def send_contact():

        kb = builder()

        kb.add(button(text="Отправить номер", request_contact=True))

        return kb.as_markup(resize_keyboard=True)