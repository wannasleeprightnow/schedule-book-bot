from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.states import UserDeskmate, UserGrade, UserNoticetime
from keyboards.default import keyboard
from keyboards.profile import builder as profile_keyboard
from services.profile import (
    get_user_profile,
    set_new_deskmate,
    set_new_grade,
    set_new_notice_time,
)

router = Router()


@router.message(F.text == "Профиль")
async def command_profile_handler(message: Message):
    telegram_user_id = message.from_user.id
    answer = await get_user_profile(telegram_user_id)
    await message.answer(
        answer, reply_markup=profile_keyboard.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data == "Изменить класс")
async def change_grade(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите класс, в котором вы учитесь.\
Например, 10А"
    )
    await state.set_state(UserGrade.grade)


@router.message(UserGrade.grade)
async def grade_choosen(message: Message, state: FSMContext):
    await state.clear()
    telegram_user_id = message.from_user.id
    answer = await set_new_grade(telegram_user_id, message.text)
    await message.answer(
        answer, reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data == "Изменить соседа по парте")
async def change_deskmate(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите username Вашего соседа по парте")
    await state.set_state(UserDeskmate.deskmate)


@router.message(UserDeskmate.deskmate)
async def deskmate_choosen(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    await state.clear()
    answer = await set_new_deskmate(telegram_user_id, message.text)
    await message.answer(
        answer, reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data == "Изменить время напоминаний")
async def change_notice_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите время напоминаний. Например, 6:00")
    await state.set_state(UserNoticetime.notice_time)


@router.message(UserNoticetime.notice_time)
async def notice_time_choosen(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    await state.clear()
    answer = await set_new_notice_time(telegram_user_id, message.text)
    await message.answer(
        answer, reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
