import asyncio
import logging
import sys

from handlers.routers import include_routers
from loader import bot, dp
from services.send_notices import send_notices
from services.send_updated_schedule import is_new_schedule_exists


async def main():
    include_routers()
    asyncio.get_event_loop().create_task(send_notices())
    asyncio.get_event_loop().create_task(is_new_schedule_exists())
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
