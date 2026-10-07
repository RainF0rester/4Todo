import uuid
import datetime
from sqlalchemy import Integer, String, Text, Date, DateTime, func, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db import Base


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subjects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True)
    finish_time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    subject: Mapped["Subject"] = relationship(
        "Subject", back_populates="stages")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "name": self.name,
            "description": self.description,
            "order": self.order,
            "start_time": self.start_time,
            "finish_time": self.finish_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
