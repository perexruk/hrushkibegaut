import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN
from routers.menu import router
from scheduler import scheduler

async def main():
    bot = Bot(token=TOKEN)

    storage = MemoryStorage()
    
    dp = Dispatcher(torage=storage)

    dp.include_router(router)

    asyncio.create_task(scheduler(bot))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())