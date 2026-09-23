# db.py
from sqlalchemy import create_engine
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
    from backend.modules.tasks import models
    from backend.modules.users import models
    from backend.modules.pomodoro import models
    Base.metadata.create_all(bind=engine, checkfirst=True)


def get_session():
    if "db_session" not in g:
        g.db_session = SessionLocal()
    return g.db_session


def close_session(e=None):
    sess = g.pop("db_session", None)
    if sess is not None:
        sess.close()
