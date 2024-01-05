import datetime

from sqlalchemy import select, and_, insert, update
from sqlalchemy.exc import MultipleResultsFound

from models import User, async_session_maker
from models import Grade, Lesson, Schedule
from schemas import ParsedSchedule


class Database:

    async def _query(self, query):
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result

    async def _stmt(self, query):
        async with async_session_maker() as session:
            await session.execute(query)
            await session.commit()

    async def add_schedule(self, schedules: list[ParsedSchedule]):
        for schedule in schedules:
            grade_id = await self.get_grade_id(schedule.number_letter_grade)
            lessons = ', '.join([await self.get_lesson_id(lesson_name)
                                 for lesson_name in schedule.lessons])
            query = (insert(Schedule)
                     .values(**{"grade_id": grade_id,
                                "lessons_date": schedule.lessons_date,
                                "lessons": lessons}
                             )
                     )
            await self._stmt(query)

    async def get_lesson_id(self, lesson_name):
        print(lesson_name)
        query_lesson = (select(Lesson)
                        .where(Lesson.input_name == lesson_name))
        result = await self._query(query_lesson)
        return str(result.scalar_one().id)

    async def get_lesson_name(self, lesson_id):
        query = (select(Lesson)
                 .where(Lesson.id == int(lesson_id)))
        result = await self._query(query)
        return result.scalar_one().correct_name

    async def format_schedule(self, lessons_ids):
        schedule = []
        for i, lesson_id in enumerate(lessons_ids.lessons.split(", "), 1):
            schedule.append(f"{i}. {await self.get_lesson_name(lesson_id)}")
        return '\n'.join(schedule)

    async def get_schedule(self, telegram_id, lessons_date):
        query = (select(User)
                 .where(User.telegram_id == telegram_id))
        result = await self._query(query)
        grade_id = result.scalar_one().grade_id
        # lessons_date = datetime.datetime.strptime(lessons_date, "%d.%m.%Y")
        query = (select(Schedule)
                 .where(and_(Schedule.lessons_date == lessons_date,
                             Schedule.grade_id == grade_id)))
        result = await self._query(query)
        return await self.format_schedule(result.scalar_one())

    async def is_deskmate_exists(self, deskmate_username):
        query = (select(User)
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
            return result.id

    async def get_grade_id(self, grade):
        grade_number = int(grade[:-1])
        grade_letter = grade[-1].upper()
        query_grade_id = (select(Grade)
                          .where(and_(
                                Grade.number == grade_number,
                                Grade.letter == grade_letter)))
        result = await self._query(query_grade_id)
        result = result.scalar_one().id
        return result

    async def get_deskmate_id(self, deskmate):
        query = (select(User)
                 .where(User.telegram_username == deskmate))
        result = await self._query(query)
        result = result.scalar_one()
        return result.id

    async def add_user(self, user_info):
        user_info["deskmate_id"] = await self.is_deskmate_exists(user_info["deskmate_username"])
        del user_info["deskmate_username"]
        user_info["grade_id"] = await self.get_grade_id(user_info["grade"])
        del user_info["grade"]
        if type(user_info["deskmate_id"]) is int:
            stmt = (insert(User)
                    .values(**user_info)
                    ).returning(User)
            user = await self._stmt(stmt)
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
