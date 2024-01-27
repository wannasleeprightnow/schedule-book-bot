from os import environ
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    TOKEN: str = environ.get("TOKEN")


@dataclass
class MailConfig:
    SENDER_MAIL = environ.get("SENDER_MAIL")
    TARGET_MAIL = environ.get("TARGET_MAIL")
    TARGET_MAIL_PASSWORD = environ.get("TARGET_MAIL_PASSWORD")
    IMAP_SERVER = "imap.mail.ru"
    CHECK_MAIL_INTERVAL = 10
    FIND_FILENAME = "Изменения в расписании"
    SAVE_FILENAME = "last_schedule.xlsx"


@dataclass
class DatabaseConfig:
    POSTGRES_USER = environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = environ.get("POSTGRES_HOST")
    POSTGRES_PORT = environ.get("POSTGRES_PORT")
    POSTGRES_DB = environ.get("POSTGRES_DB")
    CONNECT_DB = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLITE_DB = "sqlite+aiosqlite:///db.sqlite3"
