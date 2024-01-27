from asyncio import sleep

from aiogram.enums import ParseMode
import imaplib

from config import MailConfig
from loader import bot, database, schedule
from keyboards.default import keyboard
from services.parse_schedule import ScheduleExcelParser


async def is_new_schedule_exists():
    while True:
        try:
            if schedule.is_new_exists():
                await add_new_schedule(ScheduleExcelParser())
        except imaplib.IMAP4.abort:
            continue
        await sleep(MailConfig.CHECK_MAIL_INTERVAL)


async def add_new_schedule(parser: ScheduleExcelParser):
    await database.add_schedule(parser.correlate_grades_schedule())
    date = str(parser.date).split()[0]
    all_users = await database.get_all_users_telegram_id()
    for user in all_users:
        schedule = await database.get_schedule(user, date)
        await database.devide_books(user, date)
        await bot.send_message(
            user,
            f"<u>Расписание на {date}</u>\n{schedule}",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard.as_markup(resize_keyboard=True),
        )
