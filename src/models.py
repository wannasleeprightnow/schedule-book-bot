import asyncio
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    def __repr__(self):
        cols = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return " ".join(cols)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    user_type: Mapped[str] = mapped_column(default="pupil")
    telegram_id: Mapped[int]
    telegram_username: Mapped[str]
    notice_time: Mapped[datetime.time | None]
    grade_id: Mapped[int | None] = mapped_column(
        ForeignKey("grade.id", ondelete="CASCADE")
    )
    deskmate_username: Mapped[str]
    deskmate_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    grade: Mapped["Grade"] = relationship(
        back_populates="users", foreign_keys=[grade_id]
    )
    deskmate: Mapped["User"] = relationship(foreign_keys=[deskmate_id])


class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    number: Mapped[int | None]
    letter: Mapped[str | None]
    users: Mapped[list["User"]] = relationship(back_populates="grade")


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    lessons_date: Mapped[datetime.date]
    lessons: Mapped[str]
    grade_id: Mapped[int] = mapped_column(ForeignKey("grade.id", ondelete="CASCADE"))
    grade: Mapped["Grade"] = relationship(foreign_keys=[grade_id])


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    correct_name: Mapped[str]
    input_name: Mapped[str]


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    title: Mapped[str]
    author: Mapped[str]
    grade_id: Mapped[int] = mapped_column(ForeignKey("grade.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id", ondelete="CASCADE"))


class DividedBooks(Base):
    __tablename__ = "divided_books"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    first_deskmate_books: Mapped[str | None]
    second_deskmate_books: Mapped[str | None]
    first_deskmate_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    second_deskmate_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedule.id", ondelete="CASCADE")
    )


async_engine = create_async_engine(
    "sqlite+aiosqlite:///db.sqlite3",
    echo=True,
)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def create_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


# asyncio.run(create_db())
