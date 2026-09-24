import uuid
from sqlalchemy import Integer, String, DateTime, Index, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index(
            "ix_conversations_messages_fts",
            text("CAST(messages AS text) gin_trgm_ops"),
            postgresql_using="gin"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    messages: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "title": self.title,
            "messages": self.messages,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def to_json(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
