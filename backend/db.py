# db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from flask import g
from backend.config import Config


class Base(DeclarativeBase):
    pass


engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db():
    # Import models so Base is aware of them (used by Alembic env.py)
    from backend.modules.tasks import models
    from backend.modules.users import models
    from backend.modules.pomodoro import models
    from backend.modules.ai import models


def get_session():
    if "db_session" not in g:
        g.db_session = SessionLocal()
    return g.db_session


def close_session(e=None):
    sess = g.pop("db_session", None)
    if sess is not None:
        sess.close()
