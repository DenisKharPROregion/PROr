# filters.py
from aiogram.filters import Filter
from aiogram.types import Message
from config import ADMINS

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        # Проверяем, что ID пользователя, который отправил сообщение,
        # находится в списке ADMINS из вашего файла .env
        return message.from_user.id in ADMINS
