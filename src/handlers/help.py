from aiogram import F, Router
from aiogram.types import Message

from keyboards.default import keyboard

router = Router()


@router.message(F.text == "Помощь")
async def command_help_handler(message: Message):
    await message.answer(
        "Помощь", reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
