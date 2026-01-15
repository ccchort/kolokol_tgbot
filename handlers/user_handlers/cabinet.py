from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.utils.deep_linking import create_start_link
from keyboards.IKB import inlineKB as IKB
from database.db import DataBase
from database.models import User
import qrcode
import io

cab = Router()


@cab.callback_query(F.data == "personal_account")
async def personal_cabinet(callback: CallbackQuery, bot: Bot, db: DataBase):
    await callback.message.delete()
    link = await create_start_link(bot, str(callback.from_user.id), encode=True)

    qr_img = qrcode.make(link)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    qr_bytes = buf.getvalue()
    file = BufferedInputFile(qr_bytes, filename="qr.png")

    user = (await db.get_from_db(User, filters={"tg_id": callback.from_user.id}))[0]
    reg_date = user.registration_date.strftime('%d.%m.%Y')
    
    caption = (
        "<b>Твой творческий профиль</b> 🎨\n\n"
        f"<b>Дата регистрации:</b> {reg_date} {user.utm}\n"
        f"<b>Твои баллы:</b> {user.balance}\n\n"
        "<b>Этот QR-код — твой ключ в мастерскую!</b> 🔑\n"
        "Покажи его администратору на мероприятиях — и баллы твои! ✨\n\n"
        "Каждый балл — это шаг к новому творению! 🪴"
    )

    await callback.message.answer_photo(
        file,
        caption=caption,
        reply_markup=await IKB.transaction_history()
    )
    await callback.answer("✨ Вот твой личный кабинет! 🎨", show_alert=True)