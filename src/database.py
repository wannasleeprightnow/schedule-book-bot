import datetime

from sqlalchemy import and_, insert, or_, select, update
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import joinedload

from models import (async_session_maker, DividedBooks,
                    Grade, Lesson, Schedule, User)
from schemas import ParsedSchedule
from utils import divide_books


class Database:

    async def _query(self, query):
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result

    async def _stmt(self, stmt):
        async with async_session_maker() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_all_users(self):
        query = (select(User.telegram_id))
        result = await self._query(query)
        return result.scalars().all()

    async def get_profile(self, telegram_id):
        query = (select(User)
                 .where(User.telegram_id == telegram_id)
                 .options(joinedload(User.grade))
                 .options(joinedload(User.deskmate))
                 )
        result = await self._query(query)
        result = result.scalar_one()
        grade = str(result.grade.number) + result.grade.letter
        deskmate = "@" + result.deskmate.telegram_username\
            if result.deskmate else "-"
        notice_time = str(result.notice_time)[:5]\
            if result.notice_time else "-"
        return grade, deskmate, notice_time

    async def add_schedule(self, schedules: list[ParsedSchedule]):
        for schedule in schedules:
            grade_id = await self.get_grade_id(schedule.number_letter_grade)
            lessons = ', '.join([await self.get_lesson_id(lesson_name)
                                 for lesson_name in schedule.lessons])
            stmt = (insert(Schedule)
                    .values(**{"grade_id": grade_id,
                               "lessons_date": schedule.lessons_date,
                               "lessons": lessons})
                    .returning(Schedule)
                    )
            await self._stmt(stmt)

    async def get_lesson_id(self, lesson_name):
        query_lesson = (select(Lesson.id)
                        .where(Lesson.input_name == lesson_name))
        result = await self._query(query_lesson)
        result = result.scalar_one_or_none()
        return str(result) if result is not None else "0"

    async def get_lesson_name(self, lesson_id):
        query = (select(Lesson.correct_name)
                 .where(Lesson.id == int(lesson_id)))
        result = await self._query(query)
        return result.scalar_one()

    async def format_schedule(self, lessons_ids):
        return '\n'.join([f"{i}. {await self.get_lesson_name(lesson_id)}"
                          for i, lesson_id in enumerate(
                              lessons_ids.split(", "), 1)])

    async def get_schedule(self, telegram_id, lessons_date):
        query = (select(User.grade_id)
                 .where(User.telegram_id == telegram_id))
        result = await self._query(query)
        grade_id = result.scalar_one()
        query = (select(Schedule.lessons)
                 .where(and_(Schedule.lessons_date == lessons_date,
                             Schedule.grade_id == grade_id)))
        result = await self._query(query)
        return await self.format_schedule(result.scalar_one())

    async def get_schedule_dates_by_grade(self, telegram_id):
        query = (select(User.grade_id)
                 .where(User.telegram_id == telegram_id))
        result = await self._query(query)
        grade_id = result.scalar_one()
        query = (select(Schedule.lessons_date)
                 .where(Schedule.grade_id == grade_id))
        result = await self._query(query)
        return result.scalars().all()

    async def is_deskmate_exists(self, deskmate_username):
        query = (select(User.id)
                 .where(and_(User.telegram_username == deskmate_username,
                             User.deskmate_id == None))
                 )
        result = await self._query(query)
        try:
            result = result.scalar_one_or_none()
        except MultipleResultsFound:
            return "Слишком много кандидатов"
        if result is None:
            return "Ваш сосед по парте еще не начал работу с ботом"
        else:
            return result

    async def get_grade_id(self, grade):
        grade_number = int(grade[:-1])
        grade_letter = grade[-1].upper()
        query_grade_id = (select(Grade.id)
                          .where(and_(
                                Grade.number == grade_number,
                                Grade.letter == grade_letter)))
        result = await self._query(query_grade_id)
        return result.scalar_one()

    async def get_deskmate_id(self, deskmate):
        query = (select(User.id)
                 .where(User.telegram_username == deskmate))
        result = await self._query(query)
        return result.scalar_one()

    async def add_user(self, user_info):
        user_info["deskmate_id"] = await self.is_deskmate_exists(user_info["deskmate_username"])
        user_info["grade_id"] = await self.get_grade_id(user_info["grade"])
        del user_info["grade"]
        if type(user_info["deskmate_id"]) is int:
            print(user_info)
            stmt = (insert(User)
                    .values(**user_info)
                    .returning(User))
            async with async_session_maker() as session:
                user = await session.execute(stmt)
                await session.commit()
                user = user.scalar_one()
            stmt = (update(User)
                    .where(User.id == user_info["deskmate_id"])
                    .values({"deskmate_id": user.id}))
            await self._stmt(stmt)
            return "Успешно!"
        else:
            status = user_info["deskmate_id"]
            del user_info["deskmate_id"]
            stmt = (insert(User)
                    .values(**user_info)
                    )
            await self._stmt(stmt)
            return status

    async def devide_books(self, telegram_id, lessons_date):
        query = (select(User)
                 .where(User.telegram_id == telegram_id))
        result = await self._query(query)
        result = result.scalar_one()
        grade_id = result.grade_id
        user_id = result.id
        deskmate_id = result.deskmate_id
        query = (select(Schedule)
                 .where(and_(Schedule.lessons_date == lessons_date,
                             Schedule.grade_id == grade_id)))
        result = await self._query(query)
        result = result.scalar_one()
        lessons = result.lessons.split(", ")
        query = (select(DividedBooks)
                 .where(and_(or_(DividedBooks.first_deskmate_id == user_id,
                             DividedBooks.first_deskmate_id == deskmate_id),
                             DividedBooks.schedule_id == result.id),
                        ))
        check = await self._query(query)
        check = check.scalar_one_or_none()
        divided = divide_books(user_id, deskmate_id, lessons)
        divided["schedule_id"] = result.id
        if check is None:
            stmt = (insert(DividedBooks)
                    .values(**divided))
        else:
            stmt = (update(DividedBooks)
                    .values(**divided)
                    .where(and_(or_(DividedBooks.first_deskmate_id == user_id,
                                    DividedBooks.first_deskmate_id == deskmate_id),
                                DividedBooks.schedule_id == result.id),
                           )
                    )
        await self._stmt(stmt)

    async def custom_devide_books(self, telegram_id, lessons_date,
                                  books, deskmate_books):
        query = (select(User)
                 .where(User.telegram_id == telegram_id))
        result = await self._query(query)
        result = result.scalar_one()
        grade_id = result.grade_id
        user_id = result.id
        deskmate_id = result.deskmate_id
        query = (select(Schedule)
                 .where(and_(Schedule.lessons_date == lessons_date,
                             Schedule.grade_id == grade_id)))
        result = await self._query(query)
        result1 = result.scalar_one()
        lessons1 = []
        for lesson in books:
            query_lesson = (select(Lesson.id)
                            .where(Lesson.correct_name == lesson))
            result = await self._query(query_lesson)
            result = result.scalar_one_or_none()
            lessons1.append(str(result) if result is not None else "0")
        lessons2 = []
        for lesson in deskmate_books:
            query_lesson = (select(Lesson.id)
                            .where(Lesson.correct_name == lesson))
            result = await self._query(query_lesson)
            result = result.scalar_one_or_none()
            lessons2.append(str(result) if result is not None else "0")
        stmt = (update(DividedBooks)
                .values(**{"first_deskmate_books": ", ".join(lessons1),
                           "second_deskmate_books": ", ".join(lessons2),
                           "first_deskmate_id": user_id,
                           "second_deskmate_id": deskmate_id})
                .where(and_(or_(DividedBooks.first_deskmate_id == user_id,
                                DividedBooks.first_deskmate_id == deskmate_id),
                            DividedBooks.schedule_id == result1.id)
                       )
                )
        await self._stmt(stmt)

    async def get_divided_books_dates_by_grade(self, telegram_id):
        query = (select(User)
                 .where(User.telegram_id == telegram_id))
        result = await self._query(query)
        result = result.scalar_one()
        grade_id = result.grade_id
        user_id = result.id
        query = (select(Schedule)
                 .where(Schedule.grade_id == grade_id)
                 .join(DividedBooks)
                 .where(and_(or_(
                     DividedBooks.first_deskmate_id == user_id,
                     DividedBooks.second_deskmate_id == user_id
                    ),
                             DividedBooks.schedule_id == Schedule.id
                             )
                        )
                 )
        result = await self._query(query)
        result = result.scalars().all()
        return [i.lessons_date for i in result]

    async def get_divided_books(self, telegram_id, lessons_date):
        query = (select(User)
                 .where(User.telegram_id == telegram_id))
        result = await self._query(query)
        result = result.scalar_one()
        grade_id = result.grade_id
        user_id = result.id
        deskmate_id = result.deskmate_id
        query = (select(Schedule)
                 .where(and_(Schedule.lessons_date == lessons_date,
                             Schedule.grade_id == grade_id)))
        result = await self._query(query)
        result = result.scalar_one()
        query = (select(DividedBooks)
                 .where(and_(or_(DividedBooks.first_deskmate_id == user_id,
                             DividedBooks.first_deskmate_id == deskmate_id),
                             DividedBooks.schedule_id == result.id),
                        ))
        check = await self._query(query)
        check = check.scalar_one()
        books = check.first_deskmate_books if check.first_deskmate_id == user_id else check.second_deskmate_books
        schedule = []
        for i, lesson_id in enumerate(books.split(", "), 1):
            query = (select(Lesson)
                     .where(Lesson.id == int(lesson_id)))
            result = await self._query(query)
            schedule.append(f"{i}. {result.scalar_one().correct_name}")
        return '\n'.join(schedule)

    async def get_deskmate(self, telegram_id):
        query = (select(User.deskmate_id)
                 .where(User.telegram_id == telegram_id)
                 )
        result = await self._query(query)
        result = result.scalar_one()
        query = (select(User.telegram_id)
                 .where(User.id == result)
                 )
        result = await self._query(query)
        return result.scalar_one_or_none()

    async def update_user(self, telegram_id, column, value):
        stmt = (update(User)
                .where(User.telegram_id == telegram_id)
                .values({column: value}))
        await self._stmt(stmt)

    async def update_user_grade(self, telegram_id, grade):
        grade_id = await self.get_grade_id(grade)
        stmt = (update(User)
                .where(User.telegram_id == telegram_id)
                .values(**{"grade_id": grade_id}))
        await self._stmt(stmt)

    async def update_user_deskmate(self, telegram_id, deskmate):
        deskmate_id = await self.get_deskmate_id(deskmate)
        stmt = (update(User)
                .where(User.telegram_id == telegram_id)
                .values(**{"deskmate_id": deskmate_id}))
        await self._stmt(stmt)

    async def update_user_notice_time(self, telegram_id, notice_time):
        notice_time = datetime.time(*list(map(int, notice_time.split(":"))))
        stmt = (update(User)
                .where(User.telegram_id == telegram_id)
                .values(**{"notice_time": notice_time}))
        await self._stmt(stmt)
