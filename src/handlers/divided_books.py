from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards.default import keyboard
from services.divided_books import get_dates, get_divided_books
from services.profile import is_deskmate_exists
from services.schedule import get_schedule_for_handler

router = Router()


@router.message(F.text == "Что нести?")
async def command_divided_handler(message: Message):
    telegram_user_id = message.from_user.id
    dates_keyboard = await get_dates(telegram_user_id)
    await message.answer(
        "Выберите дату",
        reply_markup=dates_keyboard.adjust(1).as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data.startswith("divide_date_"))
async def divided_books_callback(callback: CallbackQuery):
    telegram_user_id = callback.from_user.id
    deskmate = await is_deskmate_exists(telegram_user_id)
    date = callback.data[12:]
    if not deskmate:
        answer = await get_schedule_for_handler(telegram_user_id, date)
    else:
        answer = await get_divided_books(telegram_user_id, date)
    await callback.message.answer(
        answer, reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
