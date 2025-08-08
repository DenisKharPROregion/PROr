# scheduler.py
import datetime
from aiogram import Bot
from sqlalchemy.orm import Session
from db import get_db, MasterClass
from aiogram_tasks import Task

async def open_registrations_task(bot: Bot):
    """Задача, которая каждый день в 10:00 открывает запись на все МК."""
    db: Session = next(get_db())
    master_classes = db.query(MasterClass).filter(MasterClass.is_open == False).all()
    
    for mc in master_classes:
        mc.is_open = True
        db.commit()
    
    if master_classes:
        # Рассылка всем администраторам
        from config import ADMINS
        for admin_id in ADMINS:
            try:
                await bot.send_message(admin_id, "📢 Запись на сегодняшние мастер-классы открыта!")
            except Exception as e:
                print(f"Failed to send message to admin {admin_id}: {e}")

async def create_tasks(bot: Bot):
    """Создает и регистрирует задачи планировщика."""
    # Задача для открытия записи каждый день в 10:00
    Task(
        open_registrations_task,
        cron='0 10 * * *', # Каждый день в 10:00
        bot=bot
    )
