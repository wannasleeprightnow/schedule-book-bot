from asyncio import sleep

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
import imaplib

from config import Config
from database import Database
from get_schedule import Schedule
from parse_xl import ScheduleExcelParser
from keyboards.default import keyboard
from main import bot

schedule_router = Router()


@schedule_router.message(F.text == "Расписание")
async def command_schedule_handler(message: Message):
    builder = InlineKeyboardBuilder()
    db = Database()
    dates = await db.get_schedule_dates_by_grade(message.from_user.id)
    for date in dates:
        builder.add(
            InlineKeyboardButton(
                text=str(date),
                callback_data="schedule_date_" + str(date)
            )
        )
    await message.answer("Выберите дату", reply_markup=builder.adjust(1).as_markup(resize_keyboard=True))


@schedule_router.message(F.text == "Что нести?")
async def command_devided_handler(message: Message):
    db = Database()
    builder = InlineKeyboardBuilder()
    dates = await db.get_divided_books_dates_by_grade(message.from_user.id)
    for date in dates:
        builder.add(
            InlineKeyboardButton(
                text=str(date),
                callback_data="divide_date_" + str(date)
            )
        )
    await message.answer("Выберите дату", reply_markup=builder.adjust(1).as_markup(resize_keyboard=True))


@schedule_router.callback_query(F.data.startswith("schedule_date_"))
async def schedule_callback(callback: CallbackQuery):
    db = Database()
    await callback.message.answer(await db.get_schedule(
        callback.from_user.id,
        callback.data[14:]),
        reply_markup=keyboard.as_markup(resize_keyboard=True)
                                  )


@schedule_router.callback_query(F.data.startswith("divide_date_"))
async def divided_books_callback(callback: CallbackQuery):
    db = Database()
    await callback.message.answer(await db.get_divided_books(
        callback.from_user.id,
        callback.data[12:]),
        reply_markup=keyboard.as_markup(resize_keyboard=True)
                                  )


@schedule_router.message(F.text == "Распределить вручную")
async def command_divide_manually_handler(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.from_user.id)
    db = Database()
    builder = InlineKeyboardBuilder()
    dates = await db.get_divided_books_dates_by_grade(message.from_user.id)
    for date in dates:
        builder.add(
            InlineKeyboardButton(
                text=str(date),
                callback_data="divide_manually_date_" + str(date)
            )
        )
    await message.answer("Выберите дату", reply_markup=builder.adjust(1).as_markup(resize_keyboard=True))


@schedule_router.callback_query(F.data.startswith("divide_manually_date_"))
async def divide_manually_callback(callback: CallbackQuery, state: FSMContext):
    db = Database()
    date = callback.data[21:]
    await state.update_data(lessons_date=date)
    await state.update_data(books=[])
    lessons = await db.get_schedule(callback.from_user.id, date)
    await state.update_data(deskmate_books=list(map(
        lambda x: ' '.join(x.split(" ")[1:]),
        lessons.split("\n"))))
    builder = InlineKeyboardBuilder()
    for lesson in lessons.split("\n"):
        builder.add(
            InlineKeyboardButton(
                text=lesson,
                callback_data="wanna_give_" + str(lesson)
            )
        )
    builder.add(InlineKeyboardButton(text="Готово", callback_data="stop"))
    await callback.message.answer(
        "Выберите предметы, учебники по которым вы хотите взять. Остальные учебники возьмет сосед по парте.",
        reply_markup=builder.adjust(1).as_markup(resize_keyboard=True)
                                  )


@schedule_router.callback_query(F.data.startswith("wanna_give_"))
async def wanna_give_book_callback(callback: CallbackQuery, state: FSMContext):
    books_ = await state.get_data()
    print(books_)
    books_ = books_["books"] + [' '.join(callback.data.split(" ")[1:])]
    await state.update_data(books=books_)


@schedule_router.callback_query(F.data.startswith("stop"))
async def stop_book_callback(callback: CallbackQuery, state: FSMContext):
    ans = await state.get_data()
    ans["books"] = list(set(ans["books"]))
    ans["deskmate_books"] = list(set(ans["deskmate_books"]) - set(ans["books"]))
    db = Database()
    res = await db.get_deskmate(ans["telegram_id"])
    await bot.send_message(res, "q")
    await db.custom_devide_books(**ans)
    await callback.message.answer("Успешно!", reply_markup=keyboard.as_markup(resize=True))
    await state.clear()


async def send_new_schedule(bot: Bot):
    schedule = Schedule()
    db = Database()
    while True:
        try:
            if schedule.get_new():
                parser = ScheduleExcelParser()
                await db.add_schedule(parser.correlate_grades_schedule())
                date = str(parser.date).split()[0]
                all_users = await db.get_all_users()
                for user in all_users:
                    schedule = await db.get_schedule(user, date)
                    await db.devide_books(user, date)
                    await bot.send_message(
                        user, f"<u>Расписание на {date}</u>\n{schedule}",
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard.as_markup(resize_keyboard=True))
        except imaplib.IMAP4.abort:
            continue
        await sleep(Config.CHECK_MAIL_INTERVAL)
