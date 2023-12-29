import asyncio
from datetime import date, time
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import Config


class Base(DeclarativeBase):
    def __repr__(self):
        cols = '\n'.join([f"{att=}" for att in self.__table__.columns.keys()])
        return f"<{self.__class__.__name__} {cols}>"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True)
    user_type: Mapped[str] = mapped_column(default="pupil")
    telegram_id: Mapped[int]
    grade_id: Mapped[int | None] = mapped_column(
        ForeignKey("grade.id", ondelete="CASCADE"))
    deskmate_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    notice_time: Mapped[time]

    grade: Mapped["Grade"] = relationship(back_populates="users")


class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    number: Mapped[int | None]
    letter: Mapped[str | None]

    users: Mapped[list["User"]] = relationship(back_populates="grade")


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True)
    correct_name: Mapped[str] = mapped_column(unique=True)
    input_name: Mapped[str]


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True)
    grade_id: Mapped[int] = mapped_column(
        ForeignKey("grade.id", ondelete="CASCADE")
    )
    lessons_date: Mapped[date]
    first_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    second_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    third_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    fourth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    fifth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    sixth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    seventh_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    eighth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    ninth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )

    lessons: Mapped[list["Lesson"]] = relationship()


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lesson.id", ondelete="CASCADE")
    )
    title: Mapped[str]
    author: Mapped[str]


class DivisionBooks(Base):
    __tablename__ = "division_books"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True)
    lessons_date: Mapped[date]
    first_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    second_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    third_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    fourth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    fifth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    sixth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    seventh_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    eighth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    ninth_lesson: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )


async_engine = create_async_engine(
    "sqlite+aiosqlite:///db.sqlite3",
    echo=True,
)

async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False
)


async def create_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
