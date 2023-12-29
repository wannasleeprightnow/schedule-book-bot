from aiogram import Router, F
from aiogram.types import Message

help_router = Router()


@help_router.message(F.text == "Помощь")
async def command_help_handler(message: Message):
    await message.answer("Помощь")
