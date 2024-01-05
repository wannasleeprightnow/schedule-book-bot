import asyncio
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    def __repr__(self):
        cols = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"\n<{self.__class__.__name__} {', '.join(cols)}>"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    user_type: Mapped[str] = mapped_column(default="pupil")
    telegram_id: Mapped[int]
    telegram_username: Mapped[str]
    grade_id: Mapped[int | None] = mapped_column(
        ForeignKey("grade.id", ondelete="CASCADE")
    )
    deskmate_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    notice_time: Mapped[datetime.time | None]
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
    grade_id: Mapped[int] = mapped_column(ForeignKey("grade.id", ondelete="CASCADE"))
    lessons_date: Mapped[datetime.date]
    lessons: Mapped[str]
    grade: Mapped["Grade"] = relationship(foreign_keys=[grade_id])


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    correct_name: Mapped[str]
    input_name: Mapped[str]

    def __repr__(self):
        return f"{self.id=} {self.correct_name=} {self.input_name=}"


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id", ondelete="CASCADE"))
    title: Mapped[str]
    author: Mapped[str]


class DivisionBooks(Base):
    __tablename__ = "division_books"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    lessons_date: Mapped[datetime.datetime]
    first_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    second_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    third_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    fourth_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    fifth_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    sixth_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    seventh_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    eighth_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    ninth_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    first_lesson: Mapped["User"] = relationship(foreign_keys=[first_lesson_id])
    second_lesson: Mapped["User"] = relationship(foreign_keys=[second_lesson_id])
    third_lesson: Mapped["User"] = relationship(foreign_keys=[third_lesson_id])
    fourth_lesson: Mapped["User"] = relationship(foreign_keys=[fourth_lesson_id])
    fifth_lesson: Mapped["User"] = relationship(foreign_keys=[fifth_lesson_id])
    sixth_lesson: Mapped["User"] = relationship(foreign_keys=[sixth_lesson_id])
    seventh_lesson: Mapped["User"] = relationship(foreign_keys=[seventh_lesson_id])
    eighth_lesson: Mapped["User"] = relationship(foreign_keys=[eighth_lesson_id])
    ninth_lesson: Mapped["User"] = relationship(foreign_keys=[ninth_lesson_id])


async_engine = create_async_engine(
    "sqlite+aiosqlite:///db.sqlite3",
    echo=True,
)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def create_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
