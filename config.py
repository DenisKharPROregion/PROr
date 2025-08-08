# config.py
import os

from dotenv import load_dotenv

load_dotenv()

# Токен вашего бота, полученный от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID администраторов
ADMINS = [int(admin_id) for admin_id in os.getenv("ADMINS", "").split(',') if admin_id]

# Путь к базе данных
DATABASE_URL = "sqlite:///./db.sqlite3"
