from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.states import AdminChangeBalance, AdminWasEvent
from keyboards.IKB import inlineKB as IKB
from database.db import DataBase
from database.models import *
from datetime import datetime

scan = Router()

# Добавить баллы
@scan.callback_query(F.data.startswith("add_balance:"))
async def add_balance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminChangeBalance.waiting_addvalue)
    user_id = int(callback.data.split(":")[1])
    await state.update_data(user_id=user_id)
    await callback.message.edit_text(
        "<b><b>Введите сумму покупки:</b> 💳",
        reply_markup=await IKB.admin_scan_cancel(user_id)
    )

@scan.message(F.text.isdigit(), AdminChangeBalance.waiting_addvalue)
async def add_user_balance(message: Message, state: FSMContext, db: DataBase):
    data = await state.get_data()
    user = await db.get_from_db(User, filters={"tg_id": data.get("user_id")})
    user = user[0]
    if 2100 <= int(message.text) < 5000:
        bonus = int(message.text) * 0.05
    elif int(message.text) >= 5000:
        bonus = int(message.text) * 0.1
    elif int(message.text) < 2100:
        return
    await db.update_db(User, filters={"tg_id": data.get("user_id")},
                     update_data={"balance": user.balance + int(bonus)})
    
    await db.add_to_db(Transaction(
        tg_id=data.get("user_id"),
        add_or_not=True,
        transaction=int(message.text),
        created_at=datetime.now().replace(tzinfo=None),
        expires_at=(datetime.now() + timedelta(days=90)).replace(tzinfo=None)
    ))
    
    await state.clear()
    await message.answer(
        f"<b>✅ +{message.text} баллов</b>\n"
        f"👤 @{user.username}"
    )
    
    await message.answer(
        f"<b>👤 @{user.username}</b>\n"
        f"Баланс: <b>{user.balance + int(bonus)}</b> баллов\n\n"
        f"<b>Действия:</b>",
        reply_markup=await IKB.admin_scan(user.tg_id)
    )

@scan.callback_query(F.data.startswith("subtract_balance:"))
async def subtract_balance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminChangeBalance.waiting_subtractvalue)
    user_id = int(callback.data.split(":")[1])
    await state.update_data(user_id=user_id)
    await callback.message.edit_text(
        "<b>Введите сумму покупки:</b> 💳",
        reply_markup=await IKB.admin_scan_cancel(user_id)
    )

@scan.message(F.text.isdigit(), AdminChangeBalance.waiting_subtractvalue)
async def subtract_user_balance(message: Message, state: FSMContext, db: DataBase):
    data = await state.get_data()
    user = await db.get_from_db(User, filters={"tg_id": data.get("user_id")})
    user = user[0]
    
    await db.update_db(User, filters={"tg_id": data.get("user_id")},
                     update_data={"balance": user.balance - float(message.text)})
    
    await db.add_to_db(Transaction(
        tg_id=data.get("user_id"),
        add_or_not=False,
        transaction=int(message.text),
        created_at=datetime.now().replace(tzinfo=None),
    ))
    
    await state.clear()
    await message.answer(
        f"<b>✅ -{message.text} баллов</b>\n"
        f"👤 @{user.username}"
    )
    
    await message.answer(
        f"<b>👤 @{user.username}</b>\n"
        f"Баланс: <b>{user.balance - int(message.text)}</b> баллов\n\n"
        f"<b>Действия:</b>",
        reply_markup=await IKB.admin_scan(user.tg_id)
    )

@scan.callback_query(F.data.startswith("was_event:"))
async def was_event(callback: CallbackQuery, db: DataBase, state: FSMContext):
    tg_id = callback.data.split(":")[1]
    await state.set_state(AdminWasEvent.add_event)
    await state.update_data(tg_id=tg_id)
    events = await db.get_from_db(Event)

    if events:
        seen = set()
        unique_events = []
        for e in events:
            if e.event_name not in seen:
                unique_events.append(e)
                seen.add(e.event_name)
        await callback.message.edit_text(#какая то хуета исправить
            "<b>🎭 Выберите мероприятие:</b>",
            reply_markup=await IKB.admin_event_kb(events=unique_events, tg_id=tg_id)
        )
    else:
        await callback.message.edit_text(
            "<b>Название мероприятия или отправьте название нового:</b> 📝",
            reply_markup=await IKB.admin_scan_cancel(tg_id)
        )

@scan.message(F.text, AdminWasEvent.add_event)
async def add_event_new(message: Message, db: DataBase, state: FSMContext):
    data = await state.get_data()
    tg_id = data.get("tg_id")

    await db.add_to_db(Event(
        tg_id=int(tg_id),
        event_name=message.text,
        created_at=datetime.now().replace(tzinfo=None)
    ))

    await message.answer(f"<b>✅ Отмечен на '{message.text}'</b>")
    await state.clear()

    user = await db.get_from_db(User, filters={"tg_id": int(tg_id)})
    user = user[0]
    await message.answer(
        f"<b>👤 @{user.username}</b>\n"
        f"Баланс: <b>{user.balance}</b> баллов\n\n"
        f"<b>Действия:</b>",
        reply_markup=await IKB.admin_scan(user.tg_id)
    )

@scan.callback_query(F.data.startswith("admin_event_page:"))
async def page_event(callback: CallbackQuery, db: DataBase):
    tg_id = callback.data.split(":")[1]
    page = callback.data.split(":")[2]
    events = await db.get_from_db(Event)

    if events:
        seen = set()
        unique_events = []
        for e in events:
            if e.event_name not in seen:
                unique_events.append(e)
                seen.add(e.event_name)
    await callback.message.edit_reply_markup(
        reply_markup=await IKB.admin_event_kb(events=unique_events, tg_id=tg_id, page=page)
    )

@scan.callback_query(F.data.startswith("add_user_event:"))
async def add_event_stock(callback: CallbackQuery, db: DataBase, state: FSMContext):
    tg_id = callback.data.split(":")[1]
    event_id = callback.data.split(":")[2]
    event = await db.get_from_db(Event, filters={"id": int(event_id)})
    event = event[0]

    await db.add_to_db(Event(
        tg_id=int(tg_id),
        event_name=event.event_name,
        created_at=datetime.now().replace(tzinfo=None)
    ))

    user = await db.get_from_db(User, filters={"tg_id": int(tg_id)})
    user = user[0]
    await callback.message.edit_text(
        f"<b>✅ Отмечен на '{event.event_name}'</b>\n"
        f"👤 @{user.username}",
        reply_markup=await IKB.admin_scan(tg_id)
    )
    await state.clear()

@scan.callback_query(F.data == "total")
async def total(callback: CallbackQuery):
    await callback.answer()

@scan.callback_query(F.data.startswith("admin_scan_cancel:"))
async def scan_cancel(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await state.clear()
    user = await db.get_from_db(User, {"tg_id": int(callback.data.split(":")[1])})
    user = user[0]
    try:
        await callback.message.edit_text(
            f"<b>👤 @{user.username}</b>\n"
            f"Баланс: <b>{user.balance}</b> баллов\n\n"
            f"<b>Действия:</b>",
            reply_markup=await IKB.admin_scan(user.tg_id)
        )
    except:
        await callback.message.delete()
        await callback.message.answer(
            f"<b>👤 @{user.username}</b>\n"
            f"Баланс: <b>{user.balance}</b> баллов\n\n"
            f"<b>Действия:</b>",
            reply_markup=await IKB.admin_scan(user.tg_id)
        )