# admin.py
import datetime
from aiogram import Router, F, Bot # <-- Вот так правильно
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.orm import Session
import pandas as pd
import io
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMINS
from db import get_db, MasterClass, Registration
from filters import IsAdmin

admin_router = Router()

# Создаем новое состояние для рассылки
class BroadcastStates(StatesGroup):
    waiting_for_message = State()

@admin_router.message(Command("add_mc"), IsAdmin())
async def add_master_class(message: Message):
    # ... (Остальной код остается без изменений)
    pass

@admin_router.message(Command("close_mc"), IsAdmin())
async def close_master_class(message: Message):
    # ... (Остальной код остается без изменений)
    pass

@admin_router.message(Command("export"), IsAdmin())
async def export_registrations(message: Message):
    # ... (Остальной код остается без изменений)
    pass

@admin_router.message(Command("broadcast"), IsAdmin())
async def start_broadcast(message: Message, state: FSMContext):
    """
    Начинает процесс рассылки.
    """
    await message.answer("Отлично, я готов к рассылке. Пришлите мне сообщение, которое нужно разослать.")
    await state.set_state(BroadcastStates.waiting_for_message)

@admin_router.message(BroadcastStates.waiting_for_message, IsAdmin())
async def send_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    """
    Рассылает сообщение всем зарегистрированным пользователям.
    """
    db: Session = next(get_db())
    
    # Получаем уникальные ID всех пользователей из таблицы регистраций
    users = db.query(Registration.user_id).distinct().all()
    
    success_count = 0
    failed_count = 0
    
    await message.answer("Начинаю рассылку. Это может занять некоторое время.")
    
    for user_id_tuple in users:
        user_id = user_id_tuple[0]
        try:
            # Копируем сообщение, чтобы сохранить форматирование, медиа и т.д.
            await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
            success_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            
    await message.answer(f"Рассылка завершена!\n\n"
                         f"✅ Успешно отправлено: {success_count}\n"
                         f"❌ Не удалось отправить: {failed_count}")
    
    await state.clear()
