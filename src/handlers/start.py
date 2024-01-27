from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from exceptions import UserHaveDeskmate, WrongGradeInput
from keyboards.default import keyboard, restart_keyboard
from loader import database
from handlers.states import UserInfo

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    telegram_id = message.from_user.id
    is_registred = await database.is_user_registered(telegram_id)
    if not is_registred:
        await message.answer("Приветственное сообщение")
        await message.answer("Введите класс, в котором вы учитесь.")
        await state.update_data(telegram_id=telegram_id,
                                telegram_username=message.from_user.username)
        await state.set_state(UserInfo.grade)
    else:
        await message.answer("Вы уже начали работу с ботом!")


@router.message(UserInfo.grade)
async def grade_choosen(message: Message, state: FSMContext):
    await message.answer("Введите username Вашего соседа по парте")
    await state.update_data(grade=message.text)
    await state.set_state(UserInfo.deskmate_username)


@router.message(UserInfo.deskmate_username)
async def deskmate_chosen(message: Message, state: FSMContext):
    await state.update_data(deskmate_username=message.text)
    user_data = await state.get_data()
    # user_data = {"telegram_id": 1000, "grade": "10А", "deskmate_username": "wannasleeprightnow", "telegram_username": "sonka_0503"}
    await state.clear()
    try:
        answer = await database.add_user(user_data)
        await message.answer(
            answer,
            reply_markup=keyboard.as_markup(resize_keyboard=True)
            )
        return
    except WrongGradeInput:
        answer = "Вы ввели класс в неверном формате! Попробуйте снова."
    except UserHaveDeskmate:
        answer = "У этого пользователя уже есть сосед по парте."
    except Exception:
        answer = "Что-то пошло не так."
    await message.answer(
            answer,
            reply_markup=restart_keyboard.as_markup(resize_keyboard=True))
