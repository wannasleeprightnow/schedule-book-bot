import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import Config
from handlers.help import help_router
from handlers.schedule import schedule_router
from handlers.start import start_router
from handlers.profile import profile_router

import get_schedule

dp = Dispatcher()


async def main() -> None:
    bot = Bot(Config.TOKEN, parse_mode=ParseMode.HTML)
    schedule = get_schedule.Schedule()
    asyncio.get_event_loop().create_task(schedule.check_new())
    dp.include_router(schedule_router)
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(profile_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
