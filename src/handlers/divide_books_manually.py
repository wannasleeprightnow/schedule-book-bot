from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loader import database
from keyboards.default import keyboard
from loader import bot

router = Router()


@router.message(F.text == "Распределить вручную")
async def command_divide_manually_handler(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.from_user.id)
    dates = await database.get_divided_books_dates_by_grade(
        message.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.add(*[InlineKeyboardButton(
        text=str(date),
        callback_data="divide_manually_date_" + str(date)) for date in dates])
    await message.answer(
        "Выберите дату",
        reply_markup=builder.adjust(1).as_markup(resize_keyboard=True))


@router.callback_query(F.data.startswith("divide_manually_date_"))
async def divide_manually_callback(callback: CallbackQuery, state: FSMContext):
    date = callback.data[21:]
    lessons = await database.get_schedule(callback.from_user.id, date)
    all_books = list(map(
        lambda x: ' '.join(x.split(" ")[1:]),
        lessons.split("\n")))
    await state.update_data(
        lessons_date=date,
        all_books=all_books,
        my_books=[],
        deskmate_books=[])
    builder = InlineKeyboardBuilder()
    builder.add(*[InlineKeyboardButton(
                text=lesson,
                callback_data="wanna_give_" + str(lesson))
                for lesson in lessons.split("\n")],
                InlineKeyboardButton(text="Готово", callback_data="stop"))
    await callback.message.answer(
        "Выберите предметы, учебники по которым вы хотите взять. Остальные \
учебники возьмет сосед по парте.",
        reply_markup=builder.adjust(1).as_markup(resize_keyboard=True)
                                  )


@router.callback_query(F.data.startswith("wanna_give_"))
async def wanna_give_book_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    my_books = data["my_books"] + [' '.join(callback.data.split(" ")[1:])]
    await state.update_data(my_books=my_books)


@router.callback_query(F.data.startswith("stop"))
async def stop_book_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data["my_books"] = list(set(data["my_books"]))
    data["deskmate_books"] = list(set(data["all_books"]) - set(
                                                            data["my_books"]))
    deskmate_telegram_id = await database.get_deskmate(data["telegram_id"])
    await bot.send_message(
        deskmate_telegram_id,
        f"{data["lessons_date"].replace("-", ".")} вам нужно взять учебники по следующим предметам:\
    \n{'\n'.join([f"{i}. {lesson}" for i, lesson in enumerate(data["deskmate_books"], start=1)])}")
    del data["all_books"]
    await database.custom_devide_books(**data)
    await callback.message.answer(
        "Успешно!",
        reply_markup=keyboard.as_markup(resize_keyboard=True))
