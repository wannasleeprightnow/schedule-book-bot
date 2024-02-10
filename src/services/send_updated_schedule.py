from asyncio import sleep
import datetime

from aiogram.utils.markdown import hbold

from config import FormatsConfig, MailConfig
from loader import bot, database, schedule
from keyboards.default import keyboard
from services.divide_books import divide_books_list
from services.schedule import get_schedule
from services.parse_schedule import ScheduleExcelParser, ParsedSchedule


async def is_new_schedule_exists():
    while True:
        try:
            if schedule.is_new_exists():
                parser = ScheduleExcelParser()
                await new_schedule(parser)
        except Exception:
            continue
        await sleep(MailConfig.CHECK_MAIL_INTERVAL)


async def new_schedule(parser: ScheduleExcelParser):
    await add_schedule(parser.correlate_grades_schedule())
    date = parser.date
    all_users_telegram_ids = await database.get_all_users_telegram_id()
    for telegram_user_id in all_users_telegram_ids:
        formated_date, schedule = await get_schedule(
            telegram_user_id, date.strftime(FormatsConfig.DATABASE_DATE_FORMAT))
        await divide_books(telegram_user_id, date)
        await bot.send_message(
            telegram_user_id,
            f"{hbold(
                f"Обновление расписания на \n{formated_date}")}\n\n{schedule}",
            reply_markup=keyboard.as_markup(resize_keyboard=True),
        )


async def add_schedule(schedules: list[ParsedSchedule]) -> None:
    for one_grade_schedule in schedules:
        grade_id = await database.get_grade_id(
            one_grade_schedule.number_letter_grade)
        lessons = ", ".join(
            list(map(str, await database.get_lessons_ids_by_input_name(
                            one_grade_schedule.lessons),
                     )
                 )
            )
        is_schedule_exists = await database.get_schedule_id(
                one_grade_schedule.lessons_date, grade_id
            )
        if is_schedule_exists is not None:
            await database.update_schedule(
                one_grade_schedule.lessons_date, grade_id, lessons
            )
        else:
            await database.insert_new_schedule(
                one_grade_schedule.lessons_date, grade_id, lessons
            )


async def divide_books(telegram_user_id: int, lessons_date: datetime.date):
    deskmate = await database.get_user_deskmate(telegram_user_id)

    if deskmate is None:
        return

    user = await database.get_user(telegram_user_id)
    lessons = list(map(str, (await database.get_lessons_ids(
        telegram_user_id, lessons_date
    )).split(", ")))
    schedule_id = await database.get_schedule_id(lessons_date, user.grade_id)

    user_books, deskmate_books = divide_books_list(lessons)
    try:
        await database.get_divided_books(user.id, user.grade_id, lessons_date)
    except Exception:
        await database.insert_divided_books(
            ", ".join(user_books), ", ".join(deskmate_books),
            user.id, deskmate.id, schedule_id
            )
    else:
        await database.add_divided_books(
            ", ".join(user_books), ", ".join(deskmate_books),
            user.id, deskmate.id, schedule_id
        )
