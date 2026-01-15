from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from database.db import DataBase
from database.models import Utm
from keyboards.IKB import inlineKB as IKB
import qrcode
import io

utm = Router()

@utm.callback_query(F.data == "add_utm")
async def add_utm(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Название метки:</b> 🎯",
        reply_markup=await IKB.admin_cancel()
    )
    await state.set_state("wait_name_utm")

@utm.message(StateFilter("wait_name_utm"))
async def wait_name_utm(message: Message, state: FSMContext, db: DataBase):
    record_id = await db.add_to_db(Utm(name=message.text))
    utm_param = f"utm_{record_id.id}"
    link = f"https://t.me/Kolokol_smr_bot?start={utm_param}"

    qr_img = qrcode.make(link)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    qr_bytes = buf.getvalue()
    file = BufferedInputFile(qr_bytes, filename="qr.png")

    await message.answer_photo(
        file,
        caption=(
            f"<b>✅ Метка создана</b>\n\n"
            f"<b>🏷️ Название:</b> {message.text}\n"
            f"<b>🔢 ID:</b> {record_id.id}\n"
            f"<b>🔗 Ссылка:</b> {link}"
        )
    )
    
    await message.answer(
        "<b>👨‍💻 Админ-панель</b>",
        reply_markup=await IKB.admin_main_menu()
    )
    await state.clear()

@utm.callback_query(F.data == "stat_utm")
async def statistics_utm(callback: CallbackQuery, db: DataBase):
    data = await db.get_from_db(Utm)
    
    if not data:
        await callback.message.edit_text(
            "<b>📭 Нет меток</b>",
            reply_markup=await IKB.admin_cancel()
        )
        return
    
    mess = "<b>📊 Статистика меток:</b>\n\n"
    for i, utm_record in enumerate(data, 1):
        mess += f"{i}. <b>{utm_record.name}</b> — {utm_record.statistics}\n"
    
    mess += "\n<b>❌ Удалить → нажми номер</b>"
    await callback.message.edit_text(mess, reply_markup=await IKB.utm_delete_keyboard(data))

@utm.callback_query(F.data.startswith("utm_delete_"))
async def delete_utm(callback: CallbackQuery, db: DataBase):
    utm_id = callback.data.split("_")[-1]
    await db.delete_from_db(Utm, filters={"id": int(utm_id)})
    await callback.answer("🗑️ Удалено", show_alert=True)
    await statistics_utm(callback, db)