import asyncio
import logging
import sys
from os import environ
from xml.etree.ElementInclude import include

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from config import Config
from models import create_db
from handlers.start import start_router
from handlers.help import help_router
from handlers.profile import profile_router
import get_schedule

dp = Dispatcher()


async def main() -> None:
    bot = Bot(Config.TOKEN, parse_mode=ParseMode.HTML)
    schedule = get_schedule.Schedule()
    # await create_db()
    asyncio.get_event_loop().create_task(schedule.check_new())
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(profile_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
