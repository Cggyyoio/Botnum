import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import init_db
from handlers import admin, user
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

async def main():
    # تهيئة قاعدة البيانات أولاً
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # تسجيل الـ routers
    dp.include_router(admin.router)
    dp.include_router(user.router)

    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())