from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class DividedBooks(Base):
    __tablename__ = "divided_books"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    first_deskmate_books: Mapped[str | None]
    second_deskmate_books: Mapped[str | None]
    first_deskmate_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    second_deskmate_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedule.id", ondelete="CASCADE")
    )
