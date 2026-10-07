import uuid
import datetime
from sqlalchemy import String, Text, Date, DateTime, UniqueConstraint, func, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db import Base


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True)
    finish_time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    stages: Mapped[list["Stage"]] = relationship(
        "Stage", back_populates="subject", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "start_time": self.start_time,
            "finish_time": self.finish_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
