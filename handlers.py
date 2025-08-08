# handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from db import get_db, MasterClass, Registration
from keyboards import main_menu_keyboard, master_class_keyboard

router = Router()

class RegistrationStates(StatesGroup):
    choosing_master_class = State()
    waiting_for_full_name = State()
    waiting_for_phone = State()

# handlers.py

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать на регистрацию мастер-классов Форума молодежи СФО 'ПРОрегион'! "
        "Выберите, что вас интересует:",
        # Было: reply_markup=main_menu_keyboard
        reply_markup=main_menu_keyboard() # <-- Добавляем скобки
    )

# ... остальной код

@router.callback_query(F.data == "register")
async def show_master_classes_to_register(callback: CallbackQuery, state: FSMContext):
    db: Session = next(get_db())
    master_classes = db.query(MasterClass).filter(MasterClass.is_open == True).all()

    if not master_classes:
        await callback.message.edit_text("На сегодня нет доступных мастер-классов.")
        await callback.answer()
        return

    await callback.message.edit_text(
        "Выберите мастер-класс для записи:",
        reply_markup=master_class_keyboard(master_classes)
    )
    await state.set_state(RegistrationStates.choosing_master_class)
    await callback.answer()

@router.callback_query(RegistrationStates.choosing_master_class)
async def process_master_class_choice(callback: CallbackQuery, state: FSMContext):
    master_class_id = int(callback.data)
    
    db: Session = next(get_db())
    registration_count = db.query(Registration).filter(
        Registration.master_class_id == master_class_id
    ).count()
    master_class = db.query(MasterClass).filter(
        MasterClass.id == master_class_id
    ).first()

    if registration_count >= master_class.max_participants:
        await callback.message.edit_text(
            f"К сожалению, на мастер-класс '{master_class.title}' все места заняты."
        )
        await state.clear()
        await callback.answer()
        return

    await state.update_data(master_class_id=master_class_id)
    await callback.message.edit_text(
        f"Вы выбрали мастер-класс '{master_class.title}'.\n\n"
        "Пожалуйста, введите ваше полное ФИО:"
    )
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.answer()

@router.message(RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text
    if not full_name or len(full_name) < 3:
        await message.answer("Пожалуйста, введите корректное ФИО.")
        return
        
    await state.update_data(full_name=full_name)
    await message.answer("Отлично! Теперь введите ваш номер телефона:")
    await state.set_state(RegistrationStates.waiting_for_phone)

@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone_number = message.text
    if not phone_number.isdigit() or len(phone_number) < 10:
        await message.answer("Пожалуйста, введите корректный номер телефона (только цифры).")
        return
    
    user_data = await state.get_data()
    master_class_id = user_data.get("master_class_id")
    full_name = user_data.get("full_name")
    
    db: Session = next(get_db())
    new_registration = Registration(
        user_id=message.from_user.id,
        master_class_id=master_class_id,
        full_name=full_name,
        phone_number=phone_number
    )
    db.add(new_registration)
    db.commit()

    master_class = db.query(MasterClass).filter(
        MasterClass.id == master_class_id
    ).first()

    await message.answer(
        f"🎉 Спасибо, {full_name}! Вы успешно записаны на мастер-класс '{master_class.title}'."
    )
    await state.clear()
