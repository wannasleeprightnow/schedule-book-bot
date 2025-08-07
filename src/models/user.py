from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.grade import Grade


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    telegram_id: Mapped[int]
    telegram_username: Mapped[str]
    notice_time: Mapped[str | None]
    grade_id: Mapped[int | None] = mapped_column(
        ForeignKey("grade.id", ondelete="CASCADE")
    )
    deskmate_username: Mapped[str | None]
    deskmate_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    grade: Mapped["Grade"] = relationship(
        back_populates="users", foreign_keys=[grade_id]
    )
    deskmate: Mapped["User"] = relationship(foreign_keys=[deskmate_id])
