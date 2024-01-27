from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from exceptions import UserDoesntExists

from loader import database
from keyboards.default import keyboard
from keyboards.profile import builder as profile_keyboard
from handlers.states import UserDeskmate, UserGrade, UserNoticetime

router = Router()


@router.message(F.text == "Профиль")
async def command_profile_handler(message: Message):
    result = await database.get_profile(message.from_user.id)
    r = await database.get_all_for_notice("06:00")
    print(r)
    await message.answer(
        f"Класс: {result[0]}\nСосед по парте: \
{result[1]}\nВремя напоминаний: {result[2]}",
        reply_markup=profile_keyboard.as_markup(resize_keyboard=True)
        )


@router.callback_query(F.data == "Изменить класс")
async def change_grade(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите класс, в котором Вы учитесь")
    await state.set_state(UserGrade.grade)


@router.message(UserGrade.grade)
async def grade_choosen(message: Message, state: FSMContext):
    await state.update_data(
        grade=message.text,
        telegram_id=message.from_user.id)
    grade = await state.get_data()
    await state.clear()
    try:
        await database.update_user_grade(**grade)
        answer = "Ваш класс обновлен"
    except Exception:
        answer = "Что-то пошло не так, проверьте корректность ввода."
    await message.answer(answer,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@router.callback_query(F.data == "Изменить соседа по парте")
async def change_deskmate(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите username Вашего соседа по парте")
    await state.set_state(UserDeskmate.deskmate)


@router.message(UserDeskmate.deskmate)
async def deskmate_choosen(message: Message, state: FSMContext):
    await state.update_data(deskmate=message.text,
                            telegram_id=message.from_user.id)
    deskmate = await state.get_data()
    await state.clear()
    try:
        await database.update_user_deskmate(**deskmate)
        answer = "Ваш сосед по парте обновлен"
    except UserDoesntExists:
        answer = "Такого пользователя не существует."
    await message.answer(answer,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@router.callback_query(F.data == "Изменить время напоминаний")
async def change_notice_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите время напоминаний")
    await state.set_state(UserNoticetime.notice_time)


@router.message(UserNoticetime.notice_time)
async def notice_time_choosen(message: Message, state: FSMContext):
    await state.update_data(notice_time=message.text,
                            telegram_id=message.from_user.id)
    notice_time = await state.get_data()
    await state.clear()
    try:
        await database.update_user_notice_time(**notice_time)
        answer = "Ваше время напоминаний обновлено"
    except Exception:
        answer = "Что-то пошло не так, проверьте корректность ввода."
    await message.answer(answer,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))
