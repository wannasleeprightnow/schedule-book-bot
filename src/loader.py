from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import BotConfig
from db.database import Database
from services.get_schedule import Schedule

dp = Dispatcher()
bot = Bot(BotConfig.TOKEN, parse_mode=ParseMode.HTML)
database = Database()
schedule = Schedule()
