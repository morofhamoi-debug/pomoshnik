import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.database import init_db
from bot.handlers import router
from bot.middlewares import AuthMiddleware

async def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN не задан в переменных окружения!")
        sys.exit(1)

    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.include_router(router)

    logging.info("Бот успешно запущен и ожидает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
