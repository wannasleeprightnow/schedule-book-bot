import datetime

from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import FormatsConfig
from keyboards.builders import dates_keyboard_builder
from loader import database


async def get_dates(telegram_user_id: int) -> InlineKeyboardBuilder:
    user = await database.get_user(telegram_user_id)
    grade_id, user_id = user.grade_id, user.id
    dates = await database.get_divided_books_dates(grade_id, user_id)
    return dates_keyboard_builder(dates, "divide_date_")


async def get_divided_books(telegram_user_id: int, date: str) -> str:
    date = datetime.datetime.strptime(
        date, FormatsConfig.DATABASE_DATE_FORMAT
    ).date()
    formated_date = date.strftime(FormatsConfig.DATE_FORMAT)
    user = await database.get_user(telegram_user_id)
    grade_id, user_id = user.grade_id, user.id
    lessons_names = await database.get_divided_books(
        user_id, grade_id, date
    )
    lessons_names = await database.get_lessons_correct_names(lessons_names)
    lessons_names = "\n".join([f"{i}. {lesson}" for i, lesson in enumerate(
        lessons_names, start=1)])
    answer = f"{hbold(f"Учебники на\n{formated_date}")}\n\n{lessons_names}"
    return answer

