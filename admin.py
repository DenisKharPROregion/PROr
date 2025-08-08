# admin.py
import datetime
from aiogram import Router, F, Bot # <-- Вот так правильно
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.orm import Session
import pandas as pd
import io
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup # <-- Добавляем State, StatesGroup

from config import ADMINS
from db import get_db, MasterClass, Registration
from filters import IsAdmin

admin_router = Router()

@admin_router.message(Command("add_mc"), IsAdmin())
async def add_master_class(message: Message):
    # Пример: /add_mc Название;Описание;100
    try:
        _, data = message.text.split(" ", 1)
        title, description, max_participants = data.split(";")
        max_participants = int(max_participants)

        db: Session = next(get_db())
        new_mc = MasterClass(
            title=title,
            description=description,
            max_participants=max_participants,
            is_open=True # По умолчанию, новый МК открыт для записи
        )
        db.add(new_mc)
        db.commit()
        await message.answer(f"✅ Мастер-класс '{title}' успешно добавлен.")
    except Exception as e:
        await message.answer(f"❌ Ошибка добавления. Используйте формат: /add_mc Название;Описание;100. Ошибка: {e}")

@admin_router.message(Command("close_mc"), IsAdmin())
async def close_master_class(message: Message):
    # Пример: /close_mc id
    try:
        _, mc_id = message.text.split(" ", 1)
        mc_id = int(mc_id)

        db: Session = next(get_db())
        master_class = db.query(MasterClass).filter(MasterClass.id == mc_id).first()
        if master_class:
            master_class.is_open = False
            db.commit()
            await message.answer(f"✅ Запись на мастер-класс '{master_class.title}' закрыта.")
        else:
            await message.answer("❌ Мастер-класс с таким ID не найден.")
    except Exception as e:
        await message.answer(f"❌ Ошибка. Используйте формат: /close_mc id")

@admin_router.message(Command("export"), IsAdmin())
async def export_registrations(message: Message):
    db: Session = next(get_db())
    registrations = db.query(Registration).all()
    
    if not registrations:
        await message.answer("Нет данных для выгрузки.")
        return

    data = [{
        "ID_записи": reg.id,
        "ФИО": reg.full_name,
        "Телефон": reg.phone_number,
        "ID_мастер-класса": reg.master_class_id,
        "Дата_записи": reg.registered_at
    } for reg in registrations]
    
    df = pd.DataFrame(data)
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    csv_buffer.seek(0)
    
    await message.answer_document(
        io.BytesIO(csv_buffer.getvalue().encode('utf-8-sig')),
        caption="Выгрузка данных по записям.",
        filename=f"registrations_{datetime.date.today()}.csv"
    )

# Создаем новое состояние для рассылки
class BroadcastStates(StatesGroup):
    waiting_for_message = State()

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
