from sqlalchemy.orm import Mapped, mapped_column

from db.db import Base


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    correct_name: Mapped[str]
    input_name: Mapped[str]
