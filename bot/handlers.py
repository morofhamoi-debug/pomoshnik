from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards import get_main_keyboard, get_back_keyboard
import sqlite3

router = Router()

# Состояния для добавления данных
class Form(StatesGroup):
    waiting_for_finance = State()
    waiting_for_task = State()
    waiting_for_goal = State()
    waiting_for_note = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Приветствую, хозяин!\n\nЯ ваш персональный мини-помощник. Выберите нужный раздел:",
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "👋 Главное меню:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

# --- ФИНАНСЫ ---
@router.callback_query(F.data == "menu_finances")
async def show_finances(callback: CallbackQuery):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, amount FROM finances WHERE user_id = ?", (callback.from_user.id,))
    rows = cursor.fetchall()
    conn.close()

    text = "💰 **Ваши финансы и копилки:**\n\n"
    if rows:
        for r in rows:
            text += f"• {r[0]}: {r[1]} руб.\n"
    else:
        text += "Пока нет записей о финансах."

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить запись", callback_data="add_finance")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "add_finance")
async def add_finance_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_finance)
    await callback.message.edit_text(
        "✍️ Введите название и сумму (например: `Зарплата 50000`):",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Form.waiting_for_finance)
async def process_finance(message: Message, state: FSMContext):
    args = message.text.rsplit(" ", 1)
    if len(args) < 2:
        await message.answer("⚠️ Пожалуйста, укажите название и сумму через пробел (например: `Накопления 5000`).")
        return
    
    title, amount_str = args[0], args[1]
    try:
        amount = float(amount_str)
    except ValueError:
        await message.answer("⚠️ Сумма должна быть числом. Попробуйте еще раз:")
        return

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO finances (user_id, type, title, amount) VALUES (?, ?, ?, ?)",
                   (message.from_user.id, 'piggy', title, amount))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer("✅ Запись успешно добавлена!", reply_markup=get_main_keyboard())

# --- ЗАДАЧИ ---
@router.callback_query(F.data == "menu_tasks")
async def show_tasks(callback: CallbackQuery):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status FROM tasks WHERE user_id = ?", (callback.from_user.id,))
    rows = cursor.fetchall()
    conn.close()

    text = "📋 **Ваши задачи:**\n\n"
    if rows:
        for r in rows:
            status_icon = "✅" if r[2] == "done" else "⏳"
            text += f"{status_icon} {r[1]}\n"
    else:
        text += "Список задач пуст."

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "add_task")
async def add_task_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_task)
    await callback.message.edit_text(
        "✍️ Введите текст новой задачи:",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.message(Form.waiting_for_task)
async def process_task(message: Message, state: FSMContext):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, status) VALUES (?, ?, ?)",
                   (message.from_user.id, message.text, 'pending'))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer("✅ Задача добавлена!", reply_markup=get_main_keyboard())

# --- ЦЕЛИ ---
@router.callback_query(F.data == "menu_goals")
async def show_goals(callback: CallbackQuery):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, target_amount, current_amount FROM goals WHERE user_id = ?", (callback.from_user.id,))
    rows = cursor.fetchall()
    conn.close()

    text = "🎯 **Ваши цели:**\n\n"
    if rows:
        for r in rows:
            text += f"• {r[0]}: {r[2]} / {r[1]} руб.\n"
    else:
        text += "Цели пока не добавлены."

    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- ЗАМЕТКИ ---
@router.callback_query(F.data == "menu_notes")
async def show_notes(callback: CallbackQuery):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM notes WHERE user_id = ?", (callback.from_user.id,))
    rows = cursor.fetchall()
    conn.close()

    text = "📝 **Ваши заметки:**\n\n"
    if rows:
        for r in rows:
            text += f"— {r[1]}\n"
    else:
        text += "Заметок пока нет."

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить заметку", callback_data="add_note")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "add_note")
async def add_note_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_note)
    await callback.message.edit_text(
        "✍️ Введите текст заметки:",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.message(Form.waiting_for_note)
async def process_note(message: Message, state: FSMContext):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (user_id, content) VALUES (?, ?)",
                   (message.from_user.id, message.text))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer("✅ Заметка сохранена!", reply_markup=get_main_keyboard())

# --- НАПОМИНАНИЯ ---
@router.callback_query(F.data == "menu_reminders")
async def show_reminders(callback: CallbackQuery):
    await callback.message.edit_text(
        "⏰ **Напоминания**\n\nФункционал активных напоминаний в разработке.",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
