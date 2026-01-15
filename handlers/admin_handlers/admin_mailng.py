import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import DataBase
from database.models import User, Event
from keyboards.IKB import inlineKB
from states.states import AdminStates
from config import config

router = Router()


@router.message(F.text == "/admin")
async def admin(message: Message):
    if message.from_user.id in config.admin_ids:
        await message.answer("👨‍💻 Админ-панель\nВыберите действие:",
                             reply_markup=await inlineKB.admin_main_menu())


@router.callback_query(F.data == "admin_back")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if callback.from_user.id in config.admin_ids:
        await callback.message.edit_text("👨‍💻 Админ-панель\nВыберите действие:",
                             reply_markup=await inlineKB.admin_main_menu())

@router.callback_query(F.data == "mailing_text")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_broadcast_text)
    await callback.message.edit_text("📝 Отправьте текст для рассылки:")


@router.callback_query(F.data == "mailing_photo")
async def start_broadcast_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_broadcast_image)
    await callback.message.edit_text("🖼 Отправьте картинку для рассылки:")

@router.callback_query(F.data == "mailing_target")
async def target(callback: CallbackQuery, db: DataBase, state: FSMContext):
    await state.set_state(AdminStates.choice_event)
    await state.update_data(target=True)
    events = await db.get_from_db(Event)

    if events:
        seen = set()
        unique_events = []
        for e in events:
            if e.event_name not in seen:
                unique_events.append(e)
                seen.add(e.event_name)
        await callback.message.edit_text(
            "<b>🎭 Выберите мероприятие:</b>",
            reply_markup=await inlineKB.admin_target_kb(events=unique_events)
        )
    else:
        await callback.answer("Похоже, никто еще не отметился на мероприятиях.\n🔕Таргетированная рассылка невозможна")

@router.callback_query(F.data.startswith("target_event:"))
async def choice_target(callback: CallbackQuery, state: FSMContext):
    event_id = callback.data.split(":")[1]
    await state.update_data(event_id=event_id)
    await callback.message.edit_text("🎯 Выберите тип рассылки", reply_markup=await inlineKB.admin_choice_type_target())

@router.callback_query(F.data.startswith("admin_target_event_page:"))
async def page_event(callback: CallbackQuery, db: DataBase):
    page = callback.data.split(":")[1]
    events = await db.get_from_db(Event)

    if events:
        seen = set()
        unique_events = []
        for e in events:
            if e.event_name not in seen:
                unique_events.append(e)
                seen.add(e.event_name)
    await callback.message.edit_reply_markup(
        reply_markup=await inlineKB.admin_target_kb(events=unique_events, page=page)
    )


### — MEDIA CAPTURE

@router.message(AdminStates.waiting_for_broadcast_image, F.photo)
async def receive_image(message: Message, state: FSMContext):
    await state.update_data(media_type="photo", file_id=message.photo[-1].file_id)
    await state.set_state(AdminStates.waiting_for_broadcast_media_text)
    await message.answer("✍️ Отправьте подпись к картинке или ❌ для отмены:",
                         reply_markup=InlineKeyboardBuilder().button(text="❌ Отмена", callback_data="admin_back").as_markup())


@router.message(AdminStates.waiting_for_broadcast_video, F.video)
async def receive_video(message: Message, state: FSMContext):
    await state.update_data(media_type="video", file_id=message.video.file_id)
    await state.set_state(AdminStates.waiting_for_broadcast_media_text)
    await message.answer("✍️ Отправьте подпись к видео или ❌ для отмены:",
                         reply_markup=InlineKeyboardBuilder().button(text="❌ Отмена", callback_data="admin_back").as_markup())


### — UNIVERSAL SENDER

@router.message(AdminStates.waiting_for_broadcast_text)
async def process_text_broadcast(message: Message, state: FSMContext, db: DataBase):
    await run_broadcast(message, state, db, text_only=True)


@router.message(AdminStates.waiting_for_broadcast_media_text)
async def process_media_broadcast(message: Message, state: FSMContext, db: DataBase):
    await run_broadcast(message, state, db, text_only=False)


### — CORE BROADCAST LOGIC

async def run_broadcast(message: Message, state: FSMContext, db: DataBase, text_only: bool = False):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Рассылка отменена", reply_markup=await inlineKB.admin_main_menu())
        return

    data = await state.get_data()
    target = data.get("target", False)
    if target:
        event_id = data.get("event_id")
        users = await db.get_from_db(Event, filters={"id": int(event_id)})
    elif not target:
        users = await db.get_from_db(User)
    success, failed = 0, 0
    status_message = await message.answer("⏳ Начинаем рассылку...")

    for user in users:
        try:
            if text_only:
                await message.bot.send_message(user.tg_id, message.text, reply_markup=await inlineKB.start_kb())
            else:
                media_type = data.get("media_type")
                file_id = data.get("file_id")
                if media_type == "photo":
                    await message.bot.send_photo(user.tg_id, photo=file_id, caption=message.text, reply_markup=await inlineKB.start_kb())
                elif media_type == "video":
                    await message.bot.send_video(user.tg_id, video=file_id, caption=message.text, reply_markup=await inlineKB.start_kb())
            success += 1
        except Exception as e:
            print(f"Failed to send to {user.tg_id}: {e}")
            failed += 1

        if (success + failed) % 5 == 0:
            await status_message.edit_text(
                f"✉️ Отправлено: {success}\n❌ Ошибок: {failed}"
            )
        await asyncio.sleep(0.07)

    await status_message.edit_text(
        f"✅ Рассылка завершена!\n\n📊 Статистика:\n✓ Успешно: {success}\n❌ Ошибок: {failed}\n📱 Всего пользователей: {len(users)}"
    )

    await state.clear()
    await message.answer("👨‍💻 Админ-панель\nВыберите действие:", reply_markup=await inlineKB.admin_main_menu())
