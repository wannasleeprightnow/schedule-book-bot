from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from keyboards.default import keyboard
from loader import database
from handlers.states import UserInfo
from services.start import register_user

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    telegram_user_id = message.from_user.id
    is_registred = await database.is_user_registered(telegram_user_id)
    if not is_registred:
        await message.answer("Привет! Этот бот поможет тебе распределять \
учебники с соседом по парте, а также всегда знать актуальное расписание. \
Больше информации в Помощь.")
        await message.answer("Введите класс, в котором вы учитесь. \
Например, 10А.")
        await state.update_data(
            telegram_id=telegram_user_id,
            telegram_username=message.from_user.username,
        )
        await state.set_state(UserInfo.grade)
    else:
        await message.answer("Вы уже начали работу с ботом!")


@router.message(UserInfo.grade)
async def grade_choosen(message: Message, state: FSMContext):
    await message.answer("Введите username Вашего соседа по парте.")
    await state.update_data(grade=message.text)
    await state.set_state(UserInfo.deskmate_telegram_username)


@router.message(UserInfo.deskmate_telegram_username)
async def deskmate_chosen(message: Message, state: FSMContext):
    await state.update_data(deskmate_telegram_username=message.text)
    user = await state.get_data()
    await state.clear()
    answer = await register_user(**user)
    await message.answer(
        answer, reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
