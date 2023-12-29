from ctypes import resize
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from keyboards.default import keyboard as default_keyboard

start_router = Router()


class UserInfo(StatesGroup):
    grade = State()
    deskmate = State()


@start_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Приветственное сообщение",
        reply_markup=default_keyboard)
    await message.answer("Введите класс, в котором вы учитесь.")
    await state.set_state(UserInfo.grade)


@start_router.message(UserInfo.grade)
async def grade_choosen(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    await message.answer("Введите имя пользователя Вашего соседа по парте")
    await state.set_state(UserInfo.deskmate)


@start_router.message(UserInfo.deskmate)
async def deskmate_chosen(message: Message, state: FSMContext):
    await state.update_data(deskmate=message.text)
    user_info = await state.get_data()
    await message.answer(f"Класс {user_info["grade"]}  Сосед {user_info["deskmate"]}")
    await state.clear()
