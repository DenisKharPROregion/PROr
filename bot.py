# bot.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db
from handlers import router
from admin import admin_router
from scheduler import create_tasks

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

    # Регистрация роутеров
    dp.include_router(router)
    dp.include_router(admin_router)

    # Запуск планировщика задач
    await create_tasks(bot)

    # Запуск бота. dp.run_polling будет блокировать выполнение, пока бот работает.
    # Если вы хотите использовать webhook, используйте dp.run_webhook
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
