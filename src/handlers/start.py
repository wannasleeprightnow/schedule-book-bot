from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from keyboards.default import keyboard as default_keyboard
from database import Database
from handlers.states import UserInfo

start_router = Router()

#! Проверка на уникальнсть


@start_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Приветственное сообщение")
    await message.answer("Введите класс, в котором вы учитесь.")
    await state.update_data(telegram_id=message.from_user.id)
    await state.update_data(telegram_username=message.from_user.username)
    await state.set_state(UserInfo.grade)


@start_router.message(UserInfo.grade)
async def grade_choosen(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    await message.answer("Введите username Вашего соседа по парте")
    await state.set_state(UserInfo.deskmate_username)


@start_router.message(UserInfo.deskmate_username)
async def deskmate_chosen(message: Message, state: FSMContext):
    await state.update_data(deskmate_username=message.text)
    user_info = await state.get_data()
    db = Database()
    res = await db.add_user(user_info)
    await message.answer(res, reply_markup=default_keyboard)
    await state.clear()
