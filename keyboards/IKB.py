from aiogram.utils.keyboard import InlineKeyboardBuilder as builder
from aiogram.types import InlineKeyboardButton as button
import math

class inlineKB:

    @staticmethod
    async def start_kb() -> builder:
        kb = builder()

        kb.row(button(text="🎨 Личный кабинет", callback_data="personal_account"))
        kb.row(button(text="📖 О нашей мастерской", callback_data="about_us"))
        kb.row(button(text="📍 Контакты", callback_data="contacts"))
        kb.row(button(text="💬 Поддержка", callback_data="support"))

        return kb.as_markup()
    
    @staticmethod
    async def back_but() -> builder:
        kb = builder()
        
        kb.add(button(text="🔙 Назад", callback_data="back"))
        
        return kb.as_markup()
    

    @staticmethod
    async def support_kb() -> builder:
        
        kb = builder()

        kb.row(button(text="💌 Написать в поддержку", url="https://t.me/kolokol_smr"))
        kb.row(button(text="🔙 Назад", callback_data="back"))

        return kb.as_markup()
    
    @staticmethod
    async def transaction_history():
        
        kb = builder()

        kb.add(button(text="📜 История транзакций", callback_data="transaction_history"))
        kb.row(button(text="🔙 Назад", callback_data="back"))

        return kb.as_markup()


    
    @staticmethod
    async def admin_main_menu():
        kb = builder()

        kb.row(button(text="📢 Рассылка (текст)", callback_data="mailing_text"))
        kb.row(button(text="🖼 Рассылка с фото", callback_data="mailing_photo"))
        kb.row(button(text="🎯 Таргетированная рассылка", callback_data="mailing_target"))
        kb.row(button(text="🎯 Добавить UTM-метку", callback_data="add_utm"))        
        kb.row(button(text="📊 Статистика меток", callback_data="stat_utm"))
        kb.row(button(text="📁 База данных", callback_data="database"))


        return kb.as_markup()
    
    @staticmethod
    async def utm_delete_keyboard(data):
            kb = builder()
            for i in enumerate(data):
                kb.row(
                    button(
                        text=f"{i[0]}", callback_data=f"utm_delete_{i[1].id}")
                )
            kb.adjust(6)
            kb.row(
                button(
                    text="❌ Выйти", callback_data="admin_back"))
            return kb.as_markup()
    

    @staticmethod
    async def admin_cancel():
         
        kb = builder()

        kb.add(button(text="❌ Выйти", callback_data="admin_back"))

        return kb.as_markup()
    
    
    @staticmethod
    async def admin_scan(tg_id):
        kb = builder()

        kb.row(button(text="💎 Добавить баллы", callback_data=f"add_balance:{tg_id}"))
        kb.row(button(text="📉 Списать баллы", callback_data=f"subtract_balance:{tg_id}"))
        kb.row(button(text="🔔 Напоминание", callback_data=f"add_remind:{tg_id}"))
        kb.row(button(text="🎭 Отметить на мероприятии", callback_data=f"was_event:{tg_id}"))
        kb.row(button(text="🚪 Выйти", callback_data="admin_back"))


        return kb.as_markup()
    
    @staticmethod
    async def admin_scan_cancel(tg_id):

        kb = builder()

        kb.row(button(text="❌ Отмена", callback_data=f"admin_scan_cancel:{tg_id}"))

        return kb.as_markup()
    
    @staticmethod
    async def admin_event_kb(events, tg_id, page=1, per_page=6):

        kb = builder()

        if not events:
            return kb.as_markup()

        total_pages = math.ceil(len(events) / per_page)

        start = (int(page) - 1) * per_page
        end = start + per_page
        page_events = events[start:end]

        for event in page_events:
            kb.add(button(text=f"{event.event_name}", callback_data=f"add_user_event:{tg_id}:{event.id}"))

        kb.adjust(2)

        # pagination
        pagination_buttons = []
        if int(page) > 1:
            pagination_buttons.append(button(text="<<", callback_data=f"admin_event_page:{tg_id}:{int(page)-1}"))

        pagination_buttons.append(button(text=f"стр. {page}/{total_pages}", callback_data="total"))

        if int(page) < total_pages:
            pagination_buttons.append(button(text=">>", callback_data=f"admin_event_page:{tg_id}:{int(page)+1}"))

        if pagination_buttons:
            kb.row(*pagination_buttons)

        kb.row(button(text="❌ Отмена", callback_data=f"admin_scan_cancel:{tg_id}"))
        

        return kb.as_markup()
    
    @staticmethod
    async def admin_target_kb(events, page=1, per_page=2):

        kb = builder()

        if not events:
            return kb.as_markup()

        total_pages = math.ceil(len(events) / per_page)

        start = (int(page) - 1) * per_page
        end = start + per_page
        page_events = events[start:end]

        for event in page_events:
            kb.add(button(text=f"{event.event_name}", callback_data=f"target_event:{event.id}"))

        kb.adjust(2)

        # pagination
        pagination_buttons = []
        if int(page) > 1:
            pagination_buttons.append(button(text="<<", callback_data=f"admin_target_event_page:{int(page)-1}"))

        pagination_buttons.append(button(text=f"стр. {page}/{total_pages}", callback_data="total"))

        if int(page) < total_pages:
            pagination_buttons.append(button(text=">>", callback_data=f"admin_target_event_page:{int(page)+1}"))

        if pagination_buttons:
            kb.row(*pagination_buttons)

        kb.row(button(text="❌ Выйти", callback_data=f"admin_back"))
        

        return kb.as_markup()

    @staticmethod
    async def admin_choice_type_target():
        kb = builder()

        kb.row(button(text="📢 Рассылка (текст)", callback_data="mailing_text"))
        kb.row(button(text="🖼 Рассылка с фото", callback_data="mailing_photo"))
        kb.row(button(text="❌ Выйти", callback_data=f"admin_back"))
        
        return kb.as_markup()