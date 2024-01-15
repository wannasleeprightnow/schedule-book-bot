from ctypes import resize
from aiogram import Router, F
from aiogram.types import Message

from keyboards.default import keyboard

help_router = Router()


@help_router.message(F.text == "Помощь")
async def command_help_handler(message: Message):
    await message.answer("Помощь", reply_markup=keyboard.as_markup(resize_keyboard=True))
