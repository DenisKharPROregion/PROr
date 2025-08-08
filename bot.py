# bot.py
import asyncio
import logging
import signal
import sys

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db
from handlers import router
from admin import admin_router
from scheduler import setup_scheduler, scheduler

async def main():
    # Инициализация логгирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Инициализация БД
    init_db()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Сначала регистрируем обычный роутер
    dp.include_router(router)
    
    # Затем регистрируем роутер для админа
    dp.include_router(admin_router)

    # Настройка и запуск планировщика задач
    setup_scheduler(bot)
    
    # Добавление обработчика для корректной остановки
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: sys.exit(0))
    loop.add_signal_handler(signal.SIGTERM, lambda: sys.exit(0))
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        # Остановка планировщика и закрытие сессии бота
        scheduler.shutdown()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
