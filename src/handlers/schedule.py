from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards.builders import dates_keyboard_builder
from keyboards.default import keyboard
from loader import database
from services.schedule import get_schedule_for_handler

router = Router()


@router.message(F.text == "Расписание")
async def command_schedule_handler(message: Message):
    telegram_user_id = message.from_user.id
    dates = await database.get_schedule_dates_by_grade(telegram_user_id)
    dates_keyboard = dates_keyboard_builder(dates, "schedule_date_")
    await message.answer(
        "Выберите дату",
        reply_markup=dates_keyboard.adjust(1).as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data.startswith("schedule_date_"))
async def schedule_callback(callback: CallbackQuery):
    telegram_user_id = callback.from_user.id
    date: str = callback.data.split("_")[2]
    answer = await get_schedule_for_handler(telegram_user_id, date)
    await callback.message.answer(
        answer,
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
