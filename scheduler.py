# scheduler.py
import datetime
from aiogram import Bot
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import get_db, MasterClass
from config import ADMINS

scheduler = AsyncIOScheduler()

async def open_registrations_task(bot: Bot):
    """
    Задача, которая каждый день в 10:00 открывает запись на все МК
    и оповещает администраторов.
    """
    db: Session = next(get_db())
    master_classes = db.query(MasterClass).filter(MasterClass.is_open == False).all()
    
    # Открытие записи
    for mc in master_classes:
        mc.is_open = True
        db.commit()
    
    # Отправка уведомлений администраторам
    if master_classes:
        for admin_id in ADMINS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text="📢 Запись на сегодняшние мастер-классы открыта!"
                )
            except Exception as e:
                print(f"Failed to send message to admin {admin_id}: {e}")

def setup_scheduler(bot: Bot):
    """
    Настраивает и запускает планировщик.
    """
    scheduler.add_job(
        open_registrations_task,
        "cron",
        hour=10,  # Запуск в 10:00 утра
        minute=0,
        args=(bot,)
    )
    scheduler.start()
