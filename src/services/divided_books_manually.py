import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold

from config import FormatsConfig
from keyboards.builders import dates_keyboard_builder
from loader import database


async def get_dates(telegram_user_id: int) -> InlineKeyboardBuilder:
    user = await database.get_user(telegram_user_id)
    grade_id, user_id = user.grade_id, user.id
    dates = await database.get_divided_books_dates(grade_id, user_id)
    return dates_keyboard_builder(dates, "redivide_")


async def get_lessons(
    telegram_user_id: int, lessons_date: datetime.date
) -> list[str]:
    lessons_ids = await database.get_lessons_ids(telegram_user_id, lessons_date)
    lessons_ids = list(map(int, lessons_ids.split(", ")))
    lessons_names = await database.get_lessons_correct_names(lessons_ids)
    return lessons_names


async def add_divided_books(user_data: dict) -> tuple:
    user_data["deskmate_books"] = set(
        user_data["all_books"] - set(user_data["user_books"])
    )
    user = await database.get_user(user_data["telegram_user_id"])
    deskmate = await database.get_user_deskmate(user_data["telegram_user_id"])
    schedule_id = await database.get_schedule_id(
        user_data["lessons_date"], user.grade_id
    )

    if deskmate is None:
        return "Что-то пошло не так."

    user_books = list(map(str, await database.get_lessons_ids_by_correct_names(
        user_data["user_books"]
    )))
    deskmate_books = list(map(str, (
        await database.get_lessons_ids_by_correct_names(
            user_data["deskmate_books"]
        )
    )))
    await database.add_divided_books(
        ", ".join(user_books), ", ".join(deskmate_books),
        deskmate.id, schedule_id, user.id
        )
    formated_date = user_data["lessons_date"].strftime(
        FormatsConfig.DATE_FORMAT)
    answer = f"{hbold(f"Перераспределение учебников на\n{formated_date}")}\
        \n\n{"\n".join([f"{i}. {lesson}" for i, lesson in enumerate(
            user_data["deskmate_books"], start=1)])}"
    return deskmate.telegram_id, answer
