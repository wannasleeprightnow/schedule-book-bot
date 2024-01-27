from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import database
from keyboards.default import keyboard

router = Router()


@router.message(F.text == "Расписание")
async def command_schedule_handler(message: Message):
    builder = InlineKeyboardBuilder()
    dates = await database.get_schedule_dates_by_grade(message.from_user.id)
    for date in dates:
        builder.add(
            InlineKeyboardButton(
                text=str(date),
                callback_data="schedule_date_" + str(date)
            )
        )
    await message.answer(
        "Выберите дату",
        reply_markup=builder.adjust(1).as_markup(resize_keyboard=True))


@router.callback_query(F.data.startswith("schedule_date_"))
async def schedule_callback(callback: CallbackQuery):
    await callback.message.answer(await database.get_schedule(
        callback.from_user.id,
        callback.data[14:]),
        reply_markup=keyboard.as_markup(resize_keyboard=True)
        )
