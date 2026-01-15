import pytz
import dateparser
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import DataBase
from database.models import Remind, User
from states.states import AdminAddRemind
from keyboards.IKB import inlineKB as IKB

remind = Router()

async def check_reminders(bot, db):
    now_moscow = datetime.now(pytz.timezone('Europe/Moscow')).replace(tzinfo=None)
    reminders = await db.get_from_db(Remind)
    
    if reminders:
        for r in reminders:
            if r.date_remind <= now_moscow:
                try:
                    await bot.send_message(
                        r.tg_id,
                        f"<b>🔔 Напоминание:</b>\n\n{r.text_remind}"
                    )
                    await db.delete_from_db(Remind, filters={"id": r.id})
                except Exception as e:
                    print(f"Ошибка: {e}")

@remind.callback_query(F.data.startswith("add_remind:"))
async def add_remind(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminAddRemind.add_text)
    tg_id = callback.data.split(":")[1]
    await state.update_data(tg_id=tg_id)
    await callback.message.edit_text(
        "<b>Текст напоминания:</b> 📝",
        reply_markup=await IKB.admin_scan_cancel(tg_id)
    )

@remind.message(F.text, AdminAddRemind.add_text)
async def add_text_remind(message: Message, state: FSMContext):
    await state.update_data(remind_text=message.text)
    await state.set_state(AdminAddRemind.add_date)
    tg_id = (await state.get_data())["tg_id"]
    await message.answer(
        "<b>Дата и время (МСК):</b> ⏰\n\n"
        "Пример: 'завтра в 15:00' или '25.12 18:30'",
        reply_markup=await IKB.admin_scan_cancel(tg_id)
    )

@remind.message(F.text, AdminAddRemind.add_date)
async def add_date_remind(message: Message, state: FSMContext, db: DataBase):
    user_data = await state.get_data()
    tz_moscow = pytz.timezone('Europe/Moscow')
    now_in_moscow = datetime.now(tz_moscow)

    parsed_date = dateparser.parse(
        message.text,
        languages=['ru'],
        settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': now_in_moscow.replace(tzinfo=None),
            'TIMEZONE': 'Europe/Moscow',
            'RETURN_AS_TIMEZONE_AWARE': False
        }
    )

    if not parsed_date:
        await message.answer(
            "<b>❌ Не распознал дату</b>\n\n"
            "Попробуй: 'завтра в 15:00'"
        )
        return

    new_remind = Remind(
        tg_id=int(user_data.get("tg_id")),
        text_remind=user_data.get("remind_text"),
        date_remind=parsed_date
    )
    await db.add_to_db(new_remind)
    
    await state.clear()
    
    formatted_date = parsed_date.strftime('%d.%m.%Y в %H:%M')
    await message.answer(
        f"<b>✅ Напоминание сохранено!</b>\n\n"
        f"Сработает: <b>{formatted_date}</b> (МСК)"
    )
    
    user = await db.get_from_db(User, {"tg_id": int(user_data.get("tg_id"))})
    user = user[0]
    await message.answer(
        f"<b>👤 @{user.username}</b>\n"
        f"Баланс: <b>{user.balance}</b> баллов\n\n"
        f"<b>Действия:</b>",
        reply_markup=await IKB.admin_scan(user.tg_id)
    )