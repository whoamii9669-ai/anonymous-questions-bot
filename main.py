from aiogram import Bot, Dispatcher

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.user import user

from config import config

import asyncio

from database.requests import create

bot = Bot(
    token=config.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

dp.include_routers(user)

async def main():
    await create() # database
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())