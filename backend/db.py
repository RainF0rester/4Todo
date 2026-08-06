# db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from flask import g
from backend.config import Config

# SQLAlchemy 2.0 style base
class Base(DeclarativeBase):
    pass

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL,
    echo=False,          # Set True to see SQL logs
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db():
    # Import models so Base can see them
    from backend.modules.tasks import models
    from backend.modules.users import models
    from backend.modules.pomodoro import models
    Base.metadata.create_all(bind=engine, checkfirst=True)
    _run_migrations()

def _run_migrations(target_engine=None):
    target_engine = target_engine or engine
    with target_engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(tasks)"))
        columns = [row[1] for row in result]
        if 'pomodoro_count' not in columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN pomodoro_count INTEGER NOT NULL DEFAULT 0"))
            conn.commit()

def get_session():
    # One session per request
    if "db_session" not in g:
        g.db_session = SessionLocal()
    return g.db_session

def close_session(e=None):
    sess = g.pop("db_session", None)
    if sess is not None:
        sess.close()