import datetime

from sqlalchemy import Integer, String, Text, Date, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

class Pomodoro(Base):
    __tablename__ = "pomodoro_records"
    __table_args__ = (UniqueConstraint("user_id", "date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "count": self.count,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "count": self.count,
        }