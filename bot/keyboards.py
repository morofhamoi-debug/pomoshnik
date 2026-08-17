from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💰 Финансы", callback_data="menu_finances"),
         InlineKeyboardButton(text="📋 Задачи", callback_data="menu_tasks")],
        [InlineKeyboardButton(text="🎯 Цели", callback_data="menu_goals"),
         InlineKeyboardButton(text="📝 Заметки", callback_data="menu_notes")],
        [InlineKeyboardButton(text="⏰ Напоминания", callback_data="menu_reminders")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    ])
