from database import Database

from aiogram import Router, F
from aiogram.types import Message

schedule_router = Router()

#! Дата расписания
#! Список дат доступных расписаний


@schedule_router.message(F.text == "Расписание")
async def command_help_handler(message: Message):
    db = Database()
    await message.answer(await db.get_schedule(message.from_user.id, "2023-11-23"))
