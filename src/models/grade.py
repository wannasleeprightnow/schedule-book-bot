from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.user import User


class Grade(Base):
    __tablename__ = "grade"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    number: Mapped[int | None]
    letter: Mapped[str | None]
    users: Mapped[list["User"]] = relationship(back_populates="grade")
