import asyncio
import logging
import sys

from handlers.help import help_router
from handlers.schedule import schedule_router, send_new_schedule
from handlers.start import start_router
from handlers.profile import profile_router
from main import bot, dp


async def main():
    dp.include_router(schedule_router)
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(profile_router)
    asyncio.get_event_loop().create_task(send_new_schedule(bot))
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
