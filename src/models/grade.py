from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base


class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    number: Mapped[int | None]
    letter: Mapped[str | None]
    users: Mapped[list["User"]] = relationship(back_populates="grade")
