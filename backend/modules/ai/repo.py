import uuid
from sqlalchemy import select, desc, text
from sqlalchemy.orm import Session
from .models import Conversation


def create_conversation(session: Session, user_id: int, title: str | None = None) -> Conversation:
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=user_id,
        title=title,
        messages=[]
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation(session: Session, conversation_id: uuid.UUID) -> Conversation | None:
    return session.get(Conversation, conversation_id)


def list_conversations(session: Session, user_id: int) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.updated_at))
    )
    return list(session.scalars(statement).all())


def update_messages(session: Session, conversation: Conversation, messages: list) -> Conversation:
    conversation.messages = messages
    session.commit()
    session.refresh(conversation)
    return conversation


def update_title(session: Session, conversation: Conversation, title: str) -> Conversation:
    conversation.title = title
    session.commit()
    session.refresh(conversation)
    return conversation


def delete_conversation(session: Session, conversation_id: uuid.UUID) -> bool:
    conversation = session.get(Conversation, conversation_id)
    if conversation is None:
        return False
    session.delete(conversation)
    session.commit()
    return True


def search_conversations(session: Session, user_id: int, query: str) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(text("CAST(messages AS text) % :query").bindparams(query=query))
        .order_by(desc(Conversation.updated_at))
    )
    return list(session.scalars(statement).all())
