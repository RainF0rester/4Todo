import pytest
from sqlalchemy import create_engine, text
from backend.db import _run_migrations


@pytest.fixture()
def old_engine():
    """Simulate a pre-migration database without pomodoro_count column."""
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY, task_title TEXT NOT NULL)"
        ))
        conn.commit()
    yield engine
    engine.dispose()


def get_columns(engine):
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(tasks)"))
        return [row[1] for row in result]


def test_migration_adds_pomodoro_count(old_engine):
    assert 'pomodoro_count' not in get_columns(old_engine)
    _run_migrations(old_engine)
    assert 'pomodoro_count' in get_columns(old_engine)


def test_migration_is_idempotent(old_engine):
    _run_migrations(old_engine)
    _run_migrations(old_engine)  # should not raise
    assert 'pomodoro_count' in get_columns(old_engine)


def test_migration_skips_if_column_exists():
    """If column already exists (new DB), migration should do nothing."""
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY, pomodoro_count INTEGER NOT NULL DEFAULT 0)"
        ))
        conn.commit()
    _run_migrations(engine)  # should not raise
    assert 'pomodoro_count' in get_columns(engine)
    engine.dispose()
