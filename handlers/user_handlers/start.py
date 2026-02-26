import dateparser
import pytz
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from keyboards.IKB import inlineKB as ikb
from database.db import DataBase
from database.models import *
from keyboards.RKB import replyKB as rkb
from states.states import AddPhoneNumber
from aiogram.utils.deep_linking import decode_payload
from utils.month_texts import texts_for_months

from config import config

start = Router()




@start.message(CommandStart(deep_link=True))
async def scan_qr(message: Message, db: DataBase, command: CommandObject, state: FSMContext):
    
    try:
        payload = decode_payload(command.args)
    except (UnicodeError, ValueError, Exception):
        payload = command.args


    if payload:
        if message.from_user.id in config.admin_ids:

            if payload.isdigit():
                user = await db.get_from_db(User, {"tg_id": int(payload)})
                user = user[0]
                await message.answer(f"Вы отсканировали QR-код пользователя @{user.username}!\nБаланс пользователя: {user.balance} баллов\n\nВыберите действие:", 
                                    reply_markup=await ikb.admin_scan(user.tg_id))
                tz_moscow = pytz.timezone('Europe/Moscow')
                now_in_moscow = datetime.now(tz_moscow)

                parsed_date = dateparser.parse(
                    "через 90 дней",
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
                    tg_id=int(user.tg_id),
                    text_remind=texts_for_months[parsed_date.month],
                    date_remind=parsed_date
                )
                await db.add_to_db(new_remind)
                
                await state.clear()

        elif message.from_user.id not in config.admin_ids and payload.isdigit():
                await message.answer("Я понимаю, интересно посмотреть закулисье, но поверь: там ничего интересного", 
                                    reply_markup=await ikb.start_kb())

        if payload.startswith("utm_"):
            try:
                utm_id = payload.split("_")[1]
                utm_data = (await db.get_from_db(Utm, filters={"id": int(utm_id)}))[0]
                await db.update_db(Utm, filters={"id": int(utm_id)},
                                update_data={"statistics": int(utm_data.statistics) + 1})
                user = await db.get_from_db(User, {"tg_id": message.from_user.id})
    
                if not user:
                    await state.set_state(AddPhoneNumber.add_phone)
                    await state.update_data(utm=utm_data.name)
                    await message.answer(
                        "<b>Привет, новый друг!</b> 🎨\n\n"
                        "Рады видеть тебя в гончарной мастерской <b>Колокол</b>!\n\n"
                        "Чтобы начать, поделись номером телефона 📱",
                        reply_markup=await rkb.send_contact()
                    )
                    return
                
                await message.answer(
                    '<b>Добро пожаловать в гончарную мастерскую "Колокол"!</b> 🔔\n\n'
                    'Здесь глина оживает в твоих руках, а каждый творческий шаг приносит радость! 💫\n\n'
                    '<b>Что бы ты хотел сделать сегодня?</b> 🎨',
                    reply_markup=await ikb.start_kb()
                )
                return
                                
            except (IndexError, ValueError):
                pass
    
        
            
    
@start.message(CommandStart())
async def start_cmd(message: Message, db: DataBase, state: FSMContext):
    await state.set_state(AddPhoneNumber.add_phone)
    user_id = message.from_user.id
    user = await db.get_from_db(User, {"tg_id": user_id})
    
    if not user:
        await message.answer(
            "<b>Привет, новый друг!</b> 🎨\n\n"
            "Рады видеть тебя в гончарной мастерской <b>Колокол</b>!\n\n"
            "Чтобы начать, поделись номером телефона 📱",
            reply_markup=await rkb.send_contact()
        )
        return
    
    await message.answer(
        '<b>Добро пожаловать в гончарную мастерскую "Колокол"!</b> 🔔\n\n'
        'Здесь глина оживает в твоих руках, а каждый творческий шаг приносит радость! 💫\n\n'
        '<b>Что бы ты хотел сделать сегодня?</b> 🎨',
        reply_markup=await ikb.start_kb()
    )

@start.message(F.contact, AddPhoneNumber.add_phone)
async def add_user(message: Message, db: DataBase, state: FSMContext):
    data = await state.get_data()
    await db.add_to_db(User(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        balance=200,
        phone=message.contact.phone_number,
        registration_date=datetime.now().replace(tzinfo=None),
        utm=data.get("utm", None)
    ))
    await db.add_to_db(Transaction(
        tg_id=message.from_user.id,
        add_or_not=True,
        transaction=200,
        created_at=datetime.now().replace(tzinfo=None),
        expires_at=datetime.now().replace(tzinfo=None) + timedelta(days=90)
    ))
    
    await state.clear()
    
    await message.answer(
        "Отлично! Регистрация завершена! 🎉\n\n"
        "Теперь ты официально творец в нашей мастерской! 🎨\n\n"
        "В честь нашего знакомства мы начислили тебе 200 приветственных баллов! Используй их, чтобы сделать свой первый шедевр еще приятнее. 🎁\n\n"
        "Добро пожаловать в мир глины, вдохновения и уютных творческих вечеров! 💫🍯",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True)
    )
    
    await message.answer(
        '<b>Снова привет!</b> 🔔\n\n'
        'Я — бот гончарной мастерской "Колокол". Помогаю отслеживать баллы, '
        'напоминаю о мероприятиях и делюсь творческими новостями! ✨\n\n'
        '<b>Куда отправимся?</b> 🎨',
        reply_markup=await ikb.start_kb()
    )

@start.callback_query(F.data == "about_us")
async def about_but(callback: CallbackQuery):
    about_text = (
        "<b>О нашей мастерской «Колокол»</b> 🎨\n\n"
        "Мы — пространство, где глина оживает в теплых руках, а каждый вращающийся круг "
        "становится центром вселенной творца. ✨\n\n"
        "<b>Почему «Колокол»?</b> 🔔\n"
        "Потому что наш колокол звонит не для тревоги, а для вдохновения! "
        "Он собирает творцов, зовёт к глине, напоминает о прекрасном.\n\n"
        "<b>Что мы делаем:</b> 💫\n"
        "• Проводим уютные мастер-классы\n"
        "• Помогаем создавать уникальную керамику\n"
        "• Собираем творческое сообщество\n"
        "• Делимся теплом и вдохновением\n\n"
        "<b>Приходи — почувствуй магию глины!</b> 🪴"
    )
    
    try:
        await callback.message.edit_text(about_text, reply_markup=await ikb.back_but())
    except:
        await callback.message.delete()
        await callback.message.answer(about_text, reply_markup=await ikb.back_but())

@start.callback_query(F.data == "contacts")
async def contacts_but(callback: CallbackQuery):
    contacts_text = (
        "<b>Как нас найти</b> 📍\n\n"
        "<b>Адрес мастерской:</b>\n"
        "г. Самара, Проспект Масленникова, 15\n\n"
        "<b>Часы работы:</b>\n"
        "Ежедневно 10:00 - 19:30\n"
        "<b>Телефон:</b>\n"
        "+7 (919) 816-69-00\n\n"
        "<b>Социальные сети:</b>\n"
        "ВК: https://vk.ru/kolokolschool_smr\n"
        "Telegram: https://t.me/kolokolschool_smr\n\n"
        "<b>Ждём тебя в гости!</b> 💫\n"
        "Приходи — напьёмся чаю и что-нибудь слепим! ☕️🎨"
    )
    
    try:
        await callback.message.edit_text(contacts_text, reply_markup=await ikb.back_but())
    except:
        await callback.message.delete()
        await callback.message.answer(contacts_text, reply_markup=await ikb.back_but())

@start.callback_query(F.data == "support")
async def sup_but(callback: CallbackQuery):
    support_text = (
        "<b>Нужна помощь? Мы рядом!</b> 💬\n\n"
        "Если у тебя:\n"
        "• 🎨 Вопрос по мастер-классам\n"
        "• 🔔 Проблема с баллами или напоминаниями\n"
        "• 💡 Идея для улучшения бота\n"
        "• ✨ Просто хочешь пообщаться о глине\n\n"
        "<b>Смело пиши нам:</b>\n"
        "👇 Нажми кнопку ниже, чтобы написать напрямую\n\n"
        "<b>Отвечаем в течение дня</b> ⏱\n"
        "☕️ Обычно с чашечкой ароматного чая в руках"
    )
    
    try:
        await callback.message.edit_text(support_text, reply_markup=await ikb.support_kb())
    except:
        await callback.message.delete()
        await callback.message.answer(support_text, reply_markup=await ikb.support_kb())


@start.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    try:
        await callback.message.edit_text('🔔 <b>Добро пожаловать в гончарную мастерскую "Колокол"!</b>\n\nЗдесь глина оживает в твоих руках, а каждый творческий шаг приносит радость! 💫\n\nЧто бы ты хотел сделать сегодня? 🎨', 
                         reply_markup=await ikb.start_kb())
    except:
        await callback.message.delete()
        await callback.message.answer('🔔 <b>Добро пожаловать в гончарную мастерскую "Колокол"!</b>\n\nЗдесь глина оживает в твоих руках, а каждый творческий шаг приносит радость! 💫\n\nЧто бы ты хотел сделать сегодня? 🎨', 
                         reply_markup=await ikb.start_kb())
