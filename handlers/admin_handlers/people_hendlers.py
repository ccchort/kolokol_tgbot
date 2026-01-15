from io import BytesIO
import pandas as pd
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from datetime import datetime

from database.db import DataBase
from database.models import User

excel = Router()


async def send_users_excel(
        message: Message,
        users_data: list,
        filename: str = 'users_report.xlsx',
        caption: str = 'Отчет по пользователям'
):
    """
    Отправляет Excel файл с данными пользователей
    """
    try:
        if not users_data:
            await message.answer("Нет данных для отчета")
            return

        # Конвертируем данные в словари
        data = []
        for user in users_data:
            user_dict = {}
            for attr in ['id', 'tg_id', 'username', 'phone', 'registration_date']:
                value = getattr(user, attr, None)
                if attr == 'registration_date' and isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                user_dict[attr.replace('_', ' ').title()] = value
            data.append(user_dict)

        # Создаем и отправляем Excel
        df = pd.DataFrame(data)
        output = BytesIO()

        # Используем openpyxl если xlsxwriter не доступен
        try:
            df.to_excel(output, index=False, engine='xlsxwriter')
        except ImportError:
            df.to_excel(output, index=False, engine='openpyxl')

        output.seek(0)
        await message.answer_document(
            BufferedInputFile(output.read(), filename=filename),
            caption=caption
        )

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        if isinstance(e, ImportError):
            await message.answer("Установите xlsxwriter: pip install xlsxwriter")


@excel.callback_query(F.data == "database")
async def get_users_report(callback: CallbackQuery, db: DataBase):
    users = await db.get_from_db(User)
    await send_users_excel(callback.message, users)