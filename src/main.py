from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import Config

dp = Dispatcher()
bot = Bot(Config.TOKEN, parse_mode=ParseMode.HTML)
