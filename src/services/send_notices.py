from asyncio import sleep
import datetime

from loader import bot, database


async def send_notices():
    while True:
        current_time = datetime.datetime.now().time()
        current_date = datetime.datetime.now().date()
        users = await database.get_all_for_notice(
            current_time.strftime("%H:%M")
        )
        if users:
            if current_time.hour > 14:
                delta = datetime.timedelta(days=1)
                lessons_date = current_date + delta
            else:
                lessons_date = current_date
            if lessons_date.weekday == 6:
                await sleep(60)
                continue
            for user in users:
                if user.deskmate_id is not None:
                    res = await database.get_divided_books(
                        user.telegram_id, lessons_date
                    )
                else:
                    res = await database.get_schedule(
                        user.telegram_id, lessons_date
                    )
                await bot.send_message(user.telegram_id, res)
        await sleep(60)
