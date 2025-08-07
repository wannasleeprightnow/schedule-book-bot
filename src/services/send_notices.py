import datetime
from asyncio import sleep

from config import FormatsConfig
from loader import bot, database
from services.divided_books import get_divided_books
from services.schedule import get_schedule_for_handler


async def send_notices():
    while True:
        current_time = datetime.datetime.now().time()
        users = await database.get_all_by_notice_time(
            current_time.strftime(FormatsConfig.TIME_FORMAT)
        )
        if users:
            lessons_date = datetime.datetime.now().date()
            if current_time.hour > 14:
                lessons_date += datetime.timedelta(days=1)
            if lessons_date.weekday == 6:
                await sleep(60)
                continue
            lessons_date = lessons_date.strftime(
                FormatsConfig.DATABASE_DATE_FORMAT
            )
            for user in users:
                deskmate = await database.get_user_deskmate(user.telegram_id)
                if deskmate is not None:
                    answer = await get_divided_books(
                        user.telegram_id, lessons_date
                    )
                else:
                    answer = await get_schedule_for_handler(
                        user.telegram_id, lessons_date
                    )
                await bot.send_message(user.telegram_id, answer)
        await sleep(60)
