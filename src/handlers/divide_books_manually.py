import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import FormatsConfig
from keyboards.builders import books_list_builder
from keyboards.default import keyboard
from loader import bot
from services.divided_books_manually import (
    add_divided_books,
    get_dates,
    get_lessons,
)
from services.profile import is_deskmate_exists

router = Router()


@router.message(F.text == "Распределить вручную")
async def command_divide_manually_handler(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    deskmate = await is_deskmate_exists(telegram_user_id)
    if not deskmate:
        await message.answer(
            "У вас нет соседа по парте.",
            reply_markup=keyboard.as_markup(resize_keyboard=True),
        )
        return
    await state.update_data(telegram_user_id=message.from_user.id)
    dates_keyboard = await get_dates(telegram_user_id)
    await message.answer(
        "Выберите дату",
        reply_markup=dates_keyboard.adjust(1).as_markup(resize_keyboard=True),
    )


@router.callback_query(F.data.startswith("redivide_"))
async def divide_manually_callback(callback: CallbackQuery, state: FSMContext):
    telegram_user_id = callback.from_user.id
    lessons_date = datetime.datetime.strptime(
        callback.data.split("_")[1], FormatsConfig.DATABASE_DATE_FORMAT
    ).date()
    lessons = await get_lessons(telegram_user_id, lessons_date)
    list_books_keyboard = books_list_builder(lessons)
    await state.update_data(
        lessons_date=lessons_date, all_books=set(lessons), user_books=[]
    )
    await callback.message.answer(
        "Выберите предметы, учебники по которым вы хотите взять. Остальные \
учебники возьмет сосед по парте.",
        reply_markup=list_books_keyboard.adjust(1).as_markup(
            resize_keyboard=True
        ),
    )


@router.callback_query(F.data.startswith("wanna_give_"))
async def wanna_give_book_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_books = data["user_books"] + [callback.data.split("_")[2]]
    await state.update_data(user_books=user_books)


@router.callback_query(F.data.startswith("stop"))
async def stop_book_callback(callback: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    await state.clear()
    await bot.send_message(*(await add_divided_books(data)))
    await callback.message.answer(
        "Успешно!", reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
