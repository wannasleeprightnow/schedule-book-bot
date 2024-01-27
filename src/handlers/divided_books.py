from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import database
from keyboards.default import keyboard

router = Router()


@router.message(F.text == "Что нести?")
async def command_devided_handler(message: Message):
    builder = InlineKeyboardBuilder()
    dates = await database.get_divided_books_dates_by_grade(
        message.from_user.id
    )
    for date in dates:
        builder.add(
            InlineKeyboardButton(
                text=str(date), callback_data="divide_date_" + str(date)
            )
        )
    await message.answer(
        "Выберите дату",
        reply_markup=builder.adjust(1).as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data.startswith("divide_date_"))
async def divided_books_callback(callback: CallbackQuery):
    await callback.message.answer(
        await database.get_divided_books(
            callback.from_user.id, callback.data[12:]
        ),
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
