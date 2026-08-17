from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from bot.config import OWNER_ID

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        if not user or user.id != OWNER_ID:
            if isinstance(event, Message):
                await event.answer("⛔ У вас нет доступа к этому боту.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Нет доступа.", show_alert=True)
            return
        return await handler(event, data)
