import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from handlers.user_handlers.start import start
from handlers.admin_handlers.admin_mailng import router as mailing
from handlers.admin_handlers.admin_utm import utm
from handlers.user_handlers.cabinet import cab
from handlers.admin_handlers.scan import scan
from handlers.user_handlers.transaction_history import history
from handlers.admin_handlers.admin_remind import remind, check_reminders
from aiogram.client.default import DefaultBotProperties
from handlers.admin_handlers.people_hendlers import excel
from database import create_tables
from database.db import DataBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    # Create tables if they don't exist
    db = DataBase()

    storage = MemoryStorage()

    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    dp = Dispatcher(storage=storage)
    dp["db"] = db

    scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))
    dp.include_routers(
                       start,
                       mailing,
                       utm,
                       cab,
                       scan,
                       history,
                       remind,
                       excel
                       )
    
    # Добавляем задачу проверки каждую минуту
    scheduler.add_job(check_reminders, "interval", minutes=1, args=(bot, db))
    
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("EXIT")
