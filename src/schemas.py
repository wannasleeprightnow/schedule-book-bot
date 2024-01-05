from dataclasses import dataclass
import datetime


@dataclass
class ParsedSchedule:

    number_letter_grade: str
    lessons_date: datetime.datetime
    lessons: list[str]
