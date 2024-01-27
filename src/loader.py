import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import BotConfig
from db.database import Database
from db.db import create_db
from services.get_schedule import Schedule
from services.parse_schedule import ScheduleExcelParser

# from repositories.grade import GradeRepository
# from repositories.user import UserRepository
# from services.grade import GradeService
# from services.user import UserService
# from db.database import create_db
# from models.devided_books import DividedBooks
# from models.grade import Grade
# from models.lesson import Lesson
# from models.schedule import Schedule
# from models.user import User
dp = Dispatcher()
bot = Bot(BotConfig.TOKEN, parse_mode=ParseMode.HTML)
database = Database()
schedule = Schedule()
# grade_repository = GradeRepository()
# user_repository = UserRepository()
# grade_service = GradeService(grade_repository)
# user_service = UserService(user_repository)

# asyncio.run(create_db())
