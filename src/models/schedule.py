from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    lessons_date = mapped_column(Date)
    lessons: Mapped[str]
    grade_id: Mapped[int] = mapped_column(
        ForeignKey("grade.id", ondelete="CASCADE")
    )
    grade: Mapped["Grade"] = relationship(foreign_keys=[grade_id])  # noqa: F821
