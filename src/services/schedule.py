import datetime

from aiogram.utils.markdown import hbold

from config import FormatsConfig
from loader import database


async def get_schedule(telegram_user_id: int, lessons_date: str) -> tuple:
    lessons_date = datetime.datetime.strptime(
        lessons_date, FormatsConfig.DATABASE_DATE_FORMAT
    ).date()
    formated_date = lessons_date.strftime(FormatsConfig.DATE_FORMAT)

    lessons_ids = await database.get_lessons_ids(
        telegram_user_id, lessons_date
    )
    lessons_ids = list(map(int, lessons_ids.split(", ")))
    lessons_names = await database.get_lessons_correct_names(lessons_ids)

    schedule = "\n".join(
        [f"{i}. {lesson}" for i, lesson in enumerate(lessons_names, start=1)]
    )
    return formated_date, schedule


async def get_schedule_for_handler(
    telegram_user_id: int, lessons_date: str
) -> str:
    formated_date, schedule = await get_schedule(
        telegram_user_id, lessons_date
    )
    answer = f"{hbold(f'Расписание на \n{formated_date}')}\n\n{schedule}"
    return answer
