import datetime

from sqlalchemy import and_, insert, or_, select, update
from sqlalchemy.orm import joinedload

from .db import async_session_maker
from models.divided_books import DividedBooks
from models.grade import Grade
from models.lesson import Lesson
from models.schedule import Schedule
from models.user import User


class Database:
    async def _query(self, query):
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result

    async def _stmt(self, stmt):
        async with async_session_maker() as session:
            await session.execute(stmt)
            await session.commit()

    async def is_user_registered(self, telegram_id: int) -> bool:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self._query(query)
        return False if result.scalars().one_or_none() is None else True

    async def get_lessons_ids(
        self, telegram_id: int, lessons_date: datetime.date
    ) -> str:
        query = (
            select(Schedule.lessons)
            .where(
                and_(
                    Schedule.lessons_date == lessons_date,
                    User.telegram_id == telegram_id,
                )
            )
            .join(User, Schedule.grade_id == User.grade_id)
        )
        lessons_ids = await self._query(query)
        return lessons_ids.scalar_one()

    async def get_lessons_correct_names(
        self, lessons_ids: list[int]
    ) -> list[str]:
        lessons_correct_names = []
        for lesson_id in lessons_ids:
            query = select(Lesson.correct_name).where(Lesson.id == lesson_id)
            lesson_correct_name = await self._query(query)
            lesson_correct_name = lesson_correct_name.scalar_one_or_none()
            lessons_correct_names.append(
                lesson_correct_name if lesson_correct_name is not None else "?"
            )
        return lessons_correct_names

    async def get_lessons_ids_by_correct_names(
        self, lessons_names_list: list[str]
    ) -> list[int]:
        lessons_ids = []
        for lessons_name in lessons_names_list:
            query = select(Lesson.id).where(Lesson.correct_name == lessons_name)
            lessons_id = await self._query(query)
            lessons_ids.append(lessons_id.scalars().first())
        return lessons_ids

    async def get_all_by_notice_time(self, now_time: str) -> list[User]:
        query = select(User).where(User.notice_time == now_time)
        result = await self._query(query)
        return result.scalars().all()

    async def get_all_users_telegram_id(self) -> list[int]:
        query = select(User.telegram_id)
        result = await self._query(query)
        return result.scalars().all()

    async def get_user_grade_and_deskmate(self, telegram_id: int) -> User:
        query = (
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(joinedload(User.grade))
            .options(joinedload(User.deskmate))
        )
        user = await self._query(query)
        return user.scalar_one()

    async def update_schedule(
        self, lessons_date: datetime.date, grade_id: int, lessons: str
    ) -> None:
        stmt = (
            update(Schedule)
            .values(lessons_date=lessons_date, lessons=lessons)
            .where(
                and_(
                    Schedule.grade_id == grade_id,
                    Schedule.lessons_date == lessons_date,
                )
            )
        )
        await self._stmt(stmt)

    async def insert_new_schedule(
        self, lessons_date: datetime.date, grade_id: int, lessons: str
    ) -> None:
        stmt = insert(Schedule).values(
            grade_id=grade_id,
            lessons_date=lessons_date,
            lessons=lessons,
        )
        await self._stmt(stmt)

    async def get_lessons_ids_by_input_name(
        self, lessons_names: list[str]
    ) -> list[int]:
        lessons_ids = []
        for lessons_name in lessons_names:
            query = select(Lesson.id).where(Lesson.input_name == lessons_name)
            result = await self._query(query)
            result = result.scalar_one_or_none()
            lessons_ids.append(result if result is not None else 0)
        return lessons_ids

    async def get_schedule_dates_by_grade(
        self, telegram_id: int
    ) -> list[datetime.date]:
        query = (
            select(Schedule.lessons_date)
            .where(Schedule.grade_id == User.grade_id)
            .join(User, User.telegram_id == telegram_id)
        )
        result = await self._query(query)
        return result.scalars().all()

    async def get_grade_id(self, grade: str) -> int | None:
        grade_number = int(grade[:-1])
        grade_letter = grade[-1].upper()
        query = select(Grade.id).where(
            and_(Grade.number == grade_number, Grade.letter == grade_letter)
        )
        grade_id = await self._query(query)
        return grade_id.scalar_one_or_none()

    async def get_deskmate(
        self, deskmate_telegram_username: str
    ) -> User | None:
        query = select(User).where(
            User.telegram_username == deskmate_telegram_username
        )
        result = await self._query(query)
        return result.scalar_one_or_none()

    async def insert_user(
        self,
        telegram_id: int,
        telegram_username: str,
        deskmate_telegram_username: str,
        grade_id: int,
        deskmate_id: int | None = None,
    ) -> User:
        stmt = (
            insert(User)
            .values(
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                deskmate_username=deskmate_telegram_username,
                grade_id=grade_id,
                deskmate_id=deskmate_id,
            )
            .returning(User.id)
        )
        async with async_session_maker() as session:
            user = await session.execute(stmt)
            await session.commit()

        return user.scalar_one()

    async def update_deskmate(self, user_id: int, deskmate_id: int) -> None:
        stmt = (
            update(User)
            .where(User.id == deskmate_id)
            .values(deskmate_id=user_id)
        )
        await self._stmt(stmt)

    async def get_schedule_id(
        self, lessons_date: datetime.date, grade_id: int
    ) -> int | None:
        query = select(Schedule.id).where(
            and_(
                Schedule.lessons_date == lessons_date,
                Schedule.grade_id == grade_id,
            )
        )
        schedule_id = await self._query(query)
        return schedule_id.scalar_one_or_none()

    async def add_divided_books(
        self,
        user_books: str,
        deskmate_books: str | None,
        deskmate_id: int | None,
        schedule_id: int,
        user_id: int,
    ) -> None:
        stmt = (
            update(DividedBooks)
            .values(
                first_deskmate_books=user_books,
                second_deskmate_books=deskmate_books,
                first_deskmate_id=user_id,
                second_deskmate_id=deskmate_id,
            )
            .where(
                and_(
                    or_(
                        DividedBooks.first_deskmate_id == user_id,
                        DividedBooks.first_deskmate_id == deskmate_id,
                    ),
                    DividedBooks.schedule_id == schedule_id,
                )
            )
        )
        await self._stmt(stmt)

    async def insert_divided_books(
        self,
        user_books: str,
        deskmate_books: str,
        user_id: int,
        deskmate_id: int,
        schedule_id: int,
    ) -> None:
        stmt = insert(DividedBooks).values(
            first_deskmate_books=user_books,
            second_deskmate_books=deskmate_books,
            first_deskmate_id=user_id,
            second_deskmate_id=deskmate_id,
            schedule_id=schedule_id,
        )
        await self._stmt(stmt)

    async def get_divided_books_dates(
        self, grade_id: int, user_id: int
    ) -> list[datetime.date]:
        query = (
            select(Schedule.lessons_date)
            .where(Schedule.grade_id == grade_id)
            .join(DividedBooks)
            .where(
                and_(
                    or_(
                        DividedBooks.first_deskmate_id == user_id,
                        DividedBooks.second_deskmate_id == user_id,
                    ),
                    DividedBooks.schedule_id == Schedule.id,
                )
            )
        )
        result = await self._query(query)
        return result.scalars().all()

    async def get_divided_books(
        self, user_id: int, grade_id: int, lessons_date: datetime.date
    ):
        query = (
            select(DividedBooks)
            .where(
                and_(
                    or_(
                        DividedBooks.first_deskmate_id == user_id,
                        DividedBooks.second_deskmate_id == user_id,
                    ),
                    DividedBooks.schedule_id == Schedule.id,
                ),
            )
            .join(Schedule)
            .where(
                and_(
                    Schedule.lessons_date == lessons_date,
                    Schedule.grade_id == grade_id,
                )
            )
        )
        result = await self._query(query)
        result = result.scalar_one()
        books = (
            result.first_deskmate_books
            if result.first_deskmate_id == user_id
            else result.second_deskmate_books
        )
        return list(map(int, books.split(", ")))

    async def update_user_grade(
        self, telegram_user_id: int, grade_id: int
    ) -> None:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_user_id)
            .values(grade_id=grade_id)
        )
        await self._stmt(stmt)

    async def get_user_deskmate(self, telegram_user_id: int) -> User | None:
        query = (
            select(User)
            .where(User.telegram_id == telegram_user_id)
            .options(joinedload(User.deskmate))
        )
        user = await self._query(query)
        user = user.scalar_one_or_none()
        if user is not None:
            return user.deskmate
        return None

    async def update_user_deskmate(
        self, telegram_user_id: int, deskmate_id: int
    ) -> int:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_user_id)
            .values(deskmate_id=deskmate_id)
        ).returning(User.id)
        async with async_session_maker() as session:
            user_id = await session.execute(stmt)
            await session.commit()
        return user_id.scalar_one()

    async def delete_user_deskmate(self, telegram_user_id: int) -> int:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_user_id)
            .values(deskmate_username=None, deskmate_id=None)
        ).returning(User.id)
        async with async_session_maker() as session:
            user_id = await session.execute(stmt)
            await session.commit()
        return user_id.scalar_one()

    async def update_deskmate_username(
        self, telegram_user_id: int, new_deskmate_username: str
    ) -> None:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_user_id)
            .values(deskmate_username=new_deskmate_username)
        )
        await self._stmt(stmt)

    async def delete_deskmate(self, telegram_user_id: int) -> None:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_user_id)
            .values(deskmate_id=None)
        )
        await self._stmt(stmt)

    async def get_user(self, telegram_user_id: int) -> User:
        query = (
            select(User)
            .where(User.telegram_id == telegram_user_id)
            .options(joinedload(User.deskmate))
        )
        user = await self._query(query)
        return user.scalar_one_or_none()

    async def update_user_notice_time(
        self, telegram_user_id: int, notice_time: datetime.time
    ) -> None:
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_user_id)
            .values(notice_time=notice_time)
        )
        await self._stmt(stmt)
