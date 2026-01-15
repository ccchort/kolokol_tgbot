from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import *
from database.db import DataBase
from keyboards.IKB import inlineKB as IKB

history = Router()

@history.callback_query(F.data == "transaction_history")
async def history_transac(callback: CallbackQuery, db: DataBase):
    transactions = await db.get_from_db(Transaction, filters={"tg_id": callback.from_user.id})
    
    if transactions:
        message_text = "<b>Твоя история баллов</b> 📜\n\n"
        
        for transaction in transactions:
            if transaction.add_or_not:
                emoji = "💚"
                sign = "+"
            else:
                emoji = "🧡"
                sign = "-"
            
            message_text += f"{emoji} {sign}{transaction.transaction} баллов\n"
        
        message_text += "\n✨ Каждый балл — шаг к новому творению!\n\n<b>Назад →</b>"
        
        await callback.message.edit_caption(caption=message_text, reply_markup=await IKB.back_but())
    else:
        await callback.answer("📭 У тебя пока нет истории транзакций!\n\nНо это исправимо — приходи на мастер-классы! 🎨", show_alert=True)