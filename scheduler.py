import asyncio
from datetime import datetime
from config import SPECIAL_DATE, LOVED_USER_ID

async def scheduler(bot):
    while True:
        now = datetime.now()
        if now >= SPECIAL_DATE:
            await bot.send_message(
                LOVED_USER_ID,
                "Ты продолжаешь стареть"
            )
            break
        await asyncio.sleep(60)