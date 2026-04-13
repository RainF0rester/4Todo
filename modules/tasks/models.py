from sqlalchemy import Integer, String, Text, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    task_title: Mapped[str] = mapped_column(String(200), nullable=False)
    task_due: Mapped[str | None] = mapped_column(String(10), nullable=True) # 'YYYY-MM-DD'
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_pinned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0/1
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # Foreign key to users.id

    is_finished: Mapped[int] = mapped_column(Integer, nullable=False ,default=0) # 0/1
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False ,default=0) # 0/1

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> dict:
        # Convert to JSON serializable dict
        return {
            "id": self.id,
            "task_title": self.task_title,
            "task_due": self.task_due,
            "task_description": self.task_description,
            "task_level": self.task_level,
            "is_pinned": self.is_pinned,
            "user_id": self.user_id,
            "is_finished": self.is_finished,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "is_deleted": self.is_deleted,
        }

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "task_title": self.task_title,
            "task_due": self.task_due,
            "task_description": self.task_description,
            "task_level": self.task_level,
            "is_finished": self.is_finished,
            "is_pinned": self.is_pinned,
        }